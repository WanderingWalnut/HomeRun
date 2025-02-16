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
        # Filter for accounts where the subtype is "checking" or "savings"
        filtered_accounts = [acc for acc in accounts if acc.get("subtype") in ["checking", "savings"]]
        return JSONResponse(content={"accounts": filtered_accounts})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/get_transactions")
async def get_transactions(data: AccessTokenRequest):
    """Fetches and processes user transactions."""
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        transactions = fetch_transactions(access_token)
        if transactions is None:
            raise HTTPException(status_code=500, detail="Failed to fetch transactions")
        # Here we separate transactions simply by category.
        spending_transactions = []
        savings_transfers = []
        for txn in transactions:
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
    Calculates the user's progress toward their weekly savings target.
    It uses transaction data from the last 7 days and distinguishes between checking and savings accounts.
      - For checking accounts, if spending is below the daily limit, the difference counts as savings.
      - For savings accounts, any positive amount is treated as a direct savings deposit.
    """
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Fetch account details to get a mapping from account_id to subtype.
        accounts_req = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_req)
        accounts = accounts_response.to_dict().get("accounts", [])
        # Build a mapping only for checking and savings accounts.
        account_types = {acc["account_id"]: acc.get("subtype") 
                         for acc in accounts if acc.get("subtype") in ["checking", "savings"]}
        
        # Fetch transactions (last 30 days) and filter for the past 7 days,
        # only including transactions from accounts in our mapping.
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
                txn_date = txn_date_val  # already a date object
            if txn_date >= week_ago and txn.get("account_id") in account_types:
                weekly_transactions.append(txn)
        
        # Define parameters.
        daily_limit = 50.0    # Example daily spending limit for checking accounts.
        weekly_target = 250.0  # Weekly savings target.
        
        # Calculate progress using account types.
        progress = calculate_progress_with_accounts(weekly_transactions, daily_limit, weekly_target, account_types)
        return JSONResponse(content=progress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_progress_with_accounts(transactions, daily_limit, weekly_target, account_types):
    """
    Calculates progress using transactions and account types:
      - For checking accounts: if spending (transactions with negative amounts) is below the daily limit, count the difference as "daily savings."
      - For savings accounts: add any positive transaction amounts as savings transfers.
    """
    from collections import defaultdict
    daily_spending = defaultdict(float)
    savings_transfers = 0.0

    for txn in transactions:
        account_id = txn.get("account_id")
        subtype = account_types.get(account_id)
        amount = txn.get("amount", 0)
        txn_date = txn.get("date")
        # For savings accounts, count positive amounts as savings deposits.
        if subtype == "savings":
            if amount > 0:
                savings_transfers += amount
        elif subtype == "checking":
            # For checking, assume spending (negative amounts) reduces the daily limit.
            # If spending is below the daily limit, the unused portion is "savings."
            # We accumulate spending per day.
            daily_spending[txn_date] += amount

    daily_savings = 0.0
    # For each day, if spending (absolute value) is less than the limit, the difference is saved.
    for day, spending in daily_spending.items():
        # Convert spending to a positive number. For instance, if spending is -30,
        # then unused is 50 - 30 = 20.
        spending_abs = abs(spending)
        if spending_abs < daily_limit:
            daily_savings += (daily_limit - spending_abs)
    
    total_progress = daily_savings + savings_transfers
    # Define one "home run" as achieving 1/10th of the weekly target.
    home_runs = total_progress / (weekly_target / 10)
    progress_percentage = (total_progress / weekly_target) * 100

    return {
        "total_progress": total_progress,
        "daily_savings": daily_savings,
        "savings_transfers": savings_transfers,
        "home_runs": home_runs,
        "progress_percentage": progress_percentage
    }

# Test writing to Firestore
try:
    doc_ref = db.collection("test").document("connection_check")
    doc_ref.set({"message": "Firebase connected successfully!"})
    print("Data written successfully!")
except Exception as e:
    print(f"Error writing to Firestore: {e}")
