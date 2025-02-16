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
    This endpoint uses the /sandbox/public_token/create endpoint to generate a public token
    for a test institution and immediately exchanges it for an access token.
    """
    try:
        # Use a valid Sandbox institution ID. 'ins_109508' is commonly used for testing.
        institution_id = "ins_109508"
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
        # Separate transactions into spending and savings transfers based on the 'category' field.
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
    It uses transaction data from the last 7 days to determine:
      - How much under the daily spending limit the user spent (daily savings)
      - How much money was deposited via transfers (savings transfers)
    These are combined to compute overall progress, a home run count, and a progress percentage.
    """
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Fetch transactions from the past 30 days and then filter to the last 7 days.
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
            if txn_date >= week_ago:
                weekly_transactions.append(txn)
        
        # Define your user's parameters.
        daily_limit = 50.0    # Example daily spend limit in dollars.
        weekly_target = 250.0  # Example weekly savings target in dollars.
        
        # Calculate progress.
        progress = calculate_progress(weekly_transactions, daily_limit, weekly_target)
        return JSONResponse(content=progress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_progress(transactions, daily_limit, weekly_target):
    """
    Calculates progress based on the provided transactions.
    - For each day, if total spending is below the daily limit, the difference is counted as "daily savings."
    - Positive transfers (identified by the category "Transfer") are added as savings transfers.
    - The total progress is the sum of daily savings and savings transfers.
    - A "home run" count is computed by dividing the total progress by one-tenth of the weekly target.
    """
    from collections import defaultdict
    daily_spending = defaultdict(float)
    savings_transfers = 0.0

    for txn in transactions:
        txn_date = txn.get("date")
        category = txn.get("category", [])
        # If the transaction is a transfer and the amount is positive, count it as a savings deposit.
        if "Transfer" in category:
            if txn.get("amount", 0) > 0:
                savings_transfers += txn.get("amount", 0)
        else:
            # For spending transactions, accumulate the amount per day.
            daily_spending[txn_date] += txn.get("amount", 0)

    daily_savings = 0.0
    # For each day, if spending is below the daily limit, add the difference to daily savings.
    for day, spending in daily_spending.items():
        if spending < daily_limit:
            daily_savings += (daily_limit - spending)
    
    total_progress = daily_savings + savings_transfers
    # For example, we define one "home run" as achieving 1/10th of the weekly target.
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
