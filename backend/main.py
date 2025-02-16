from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime, timedelta
from plaid_service import plaid_client, fetch_transactions
from firebase_service import db  # Ensure firebase_service.py is correctly configured
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.accounts_get_request import AccountsGetRequest

app = FastAPI()

# Define a Pydantic model for endpoints that require an access token.
class AccessTokenRequest(BaseModel):
    access_token: str

@app.get("/")
async def home():
    return {"message": "Hackathon API is running!"}

@app.get("/api/generate_public_token")
async def generate_public_token():
    """
    Generates a public token in the Sandbox and then exchanges it for an access token.
    """
    try:
        institution_id = "ins_109508"  # Sandbox test institution
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[Products('transactions')]
        )
        pt_response = plaid_client.sandbox_public_token_create(pt_request)
        public_token = pt_response.to_dict()["public_token"]

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.to_dict()["access_token"]
        item_id = exchange_response.to_dict()["item_id"]

        return JSONResponse(content={
            "public_token": public_token,
            "access_token": access_token,
            "item_id": item_id
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/exchange_public_token")
async def exchange_public_token(request: Request):
    """Exchanges a public token for an access token."""
    try:
        data = await request.json()
        public_token = data.get("public_token")
        if not public_token:
            raise HTTPException(status_code=400, detail="Public token is required")
        request_body = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request_body)
        access_token = response["access_token"]
        item_id = response["item_id"]
        print(f"Access Token: {access_token}, Item ID: {item_id}")
        return JSONResponse(content={"access_token": access_token, "item_id": item_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/accounts")
async def get_accounts(data: AccessTokenRequest):
    """
    Retrieves account details for the given access token, filtered to only checking and savings accounts.
    """
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        request_body = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request_body)
        accounts = response.to_dict().get("accounts", [])
        # Filter for accounts with subtype "checking" or "savings"
        filtered_accounts = [acc for acc in accounts if acc.get("subtype") in ["checking", "savings"]]
        return JSONResponse(content={"accounts": filtered_accounts})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/get_transactions")
async def get_transactions(data: AccessTokenRequest):
    """
    Fetches transactions only from checking and savings accounts.
    """
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Retrieve account mapping (account_id -> subtype) for checking/savings accounts.
        accounts_req = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_req)
        accounts = accounts_response.to_dict().get("accounts", [])
        account_types = {acc["account_id"]: acc.get("subtype")
                         for acc in accounts if acc.get("subtype") in ["checking", "savings"]}
        
        # Fetch transactions (last 30 days)
        transactions = fetch_transactions(access_token)
        if transactions is None:
            raise HTTPException(status_code=500, detail="Failed to fetch transactions")
        
        # Filter transactions to include only those from our checking/savings accounts.
        filtered_transactions = [txn for txn in transactions if txn.get("account_id") in account_types]
        
        # Separate transactions based on category.
        spending_transactions = []
        savings_transfers = []
        for txn in filtered_transactions:
            if "Transfer" in txn.get("category", []):
                savings_transfers.append(txn)
            else:
                spending_transactions.append(txn)
        
        response_content = jsonable_encoder({
            "spending_transactions": spending_transactions,
            "savings_transfers": savings_transfers
        })
        return JSONResponse(content=response_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/update_progress")
async def update_progress(data: AccessTokenRequest):
    """
    Calculates the user's progress toward their weekly savings target using transactions
    only from checking and savings accounts.
    
    For checking accounts:
      - Spending reduces the daily limit.
      - If spending is below the daily limit (set at $50), the unused portion is counted as savings.
    
    For savings accounts:
      - Any positive transaction amount is treated as a direct savings deposit.
    
    Weekly target is set at $250 (i.e., if the user saves $250 in a week, that's 1 home run).
    The down payment (total target) is $20,000. Thus, the user needs 80 weekly home runs to hit the goal.
    """
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Get account mapping for checking and savings.
        accounts_req = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_req)
        accounts = accounts_response.to_dict().get("accounts", [])
        account_types = {acc["account_id"]: acc.get("subtype")
                         for acc in accounts if acc.get("subtype") in ["checking", "savings"]}
        
        # Fetch transactions (last 30 days) and then filter for the past 7 days and our accounts.
        transactions = fetch_transactions(access_token)
        if transactions is None:
            raise HTTPException(status_code=500, detail="Failed to fetch transactions")
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        weekly_transactions = []
        for txn in transactions:
            txn_date_val = txn.get("date")
            if isinstance(txn_date_val, str):
                txn_date = datetime.strptime(txn_date_val, "%Y-%m-%d").date()
            else:
                txn_date = txn_date_val
            if txn_date >= week_ago and txn.get("account_id") in account_types:
                weekly_transactions.append(txn)
        
        # Define parameters.
        daily_limit = 50.0         # Daily spending limit for checking accounts.
        weekly_target = 250.0       # Weekly savings target (i.e., $250 saved = 1 home run for the week).
        down_payment_target = 20000.0  # Overall target (e.g., down payment of $20,000).
        
        # Calculate progress.
        progress = calculate_progress_with_accounts(weekly_transactions, daily_limit, weekly_target, account_types, down_payment_target)
        return JSONResponse(content=progress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_progress_with_accounts(transactions, daily_limit, weekly_target, account_types, down_payment_target):
    """
    Calculates progress using transactions and account types:
      - For checking accounts: If the total spending in a day (absolute value) is below the daily limit,
        the unused portion is considered savings.
      - For savings accounts: Any positive transaction is added as a direct savings deposit.
    
    Returns:
      - weekly_progress: Total savings accumulated in the week.
      - weekly_home_runs: Number of "home runs" achieved this week (weekly_progress / weekly_target).
      - weekly_progress_percentage: (weekly_progress / weekly_target) * 100.
      - down_payment_target: Overall goal (e.g., $20,000).
      - home_runs_needed: Total home runs required to hit the down payment target (down_payment_target / weekly_target).
    """
    from collections import defaultdict
    daily_spending = defaultdict(float)
    savings_transfers = 0.0

    for txn in transactions:
        account_id = txn.get("account_id")
        subtype = account_types.get(account_id)
        amount = txn.get("amount", 0)
        txn_date = txn.get("date")
        if subtype == "savings":
            # For savings accounts, count positive amounts as savings deposits.
            if amount > 0:
                savings_transfers += amount
        elif subtype == "checking":
            # For checking, accumulate spending per day.
            daily_spending[txn_date] += amount

    daily_savings = 0.0
    for day, spending in daily_spending.items():
        spending_abs = abs(spending)
        if spending_abs < daily_limit:
            daily_savings += (daily_limit - spending_abs)
    
    weekly_progress = daily_savings + savings_transfers
    weekly_home_runs = weekly_progress / weekly_target
    home_runs_needed = down_payment_target / weekly_target
    weekly_progress_percentage = (weekly_progress / weekly_target) * 100

    return {
        "weekly_progress": weekly_progress,
        "daily_savings": daily_savings,
        "savings_transfers": savings_transfers,
        "weekly_home_runs": weekly_home_runs,
        "weekly_progress_percentage": weekly_progress_percentage,
        "weekly_target": weekly_target,
        "down_payment_target": down_payment_target,
        "home_runs_needed": home_runs_needed
    }

# Test writing to Firestore
try:
    doc_ref = db.collection("test").document("connection_check")
    doc_ref.set({"message": "Firebase connected successfully!"})
    print("Data written successfully!")
except Exception as e:
    print(f"Error writing to Firestore: {e}")
