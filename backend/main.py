import os 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime, timedelta
from plaid_service import plaid_client, fetch_transactions
from firebase_service import db  # Firestore client (from your firebase_service.py)
from firebase_admin import auth  # Import Firebase Admin auth
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.accounts_get_request import AccountsGetRequest
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Allow all origins for testing; in production, restrict this to your actual front end domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model for endpoints that require an access token.
class AccessTokenRequest(BaseModel):
    access_token: str

# Extend that model for endpoints that need Firebase authentication
class UserRequest(AccessTokenRequest):
    firebase_token: str

# Define a model for creating a new Firebase user
class CreateUserRequest(BaseModel):
    email: str
    password: str

# Make sure your Firebase API key is available in your environment
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
if not FIREBASE_API_KEY:
    raise Exception("FIREBASE_API_KEY is not set in your environment.")

# Pydantic model for login requests
class LoginRequest(BaseModel):
    email: str
    password: str



@app.get("/")
async def home():
    return {"message": "Hackathon API is running!"}

@app.get("/api/generate_public_token")
async def generate_public_token():
    try:
        institution_id = "ins_109508"  # Sandbox test institution
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[Products("transactions")]
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
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        request_body = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request_body)
        accounts = response.to_dict().get("accounts", [])
        filtered_accounts = [acc for acc in accounts if acc.get("subtype") in ["checking", "savings"]]
        return JSONResponse(content={"accounts": filtered_accounts})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/get_transactions")
async def get_transactions(data: AccessTokenRequest):
    try:
        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        accounts_req = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_req)
        accounts = accounts_response.to_dict().get("accounts", [])
        account_types = {acc["account_id"]: acc.get("subtype")
                         for acc in accounts if acc.get("subtype") in ["checking", "savings"]}
        
        transactions = fetch_transactions(access_token)
        if transactions is None:
            raise HTTPException(status_code=500, detail="Failed to fetch transactions")
        
        filtered_transactions = [txn for txn in transactions if txn.get("account_id") in account_types]
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
async def update_progress(data: UserRequest):
    """
    Calculates the user's weekly progress toward their savings target using Plaid transactions,
    then stores that data in Firestore under the authenticated user's document.
    
    The request expects:
      - access_token: the Plaid access token
      - firebase_token: a Firebase ID token obtained after the user signs in
    """
    try:
        # Verify Firebase token and get the UID
        decoded_token = auth.verify_id_token(data.firebase_token)
        uid = decoded_token.get("uid")
        if not uid:
            raise HTTPException(status_code=401, detail="Unable to verify user.")

        access_token = data.access_token
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        # Retrieve account details from Plaid (checking/savings only)
        accounts_req = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_req)
        accounts = accounts_response.to_dict().get("accounts", [])
        account_types = {acc["account_id"]: acc.get("subtype")
                         for acc in accounts if acc.get("subtype") in ["checking", "savings"]}
        
        # Fetch transactions (last 30 days) and filter for the past 7 days from our accounts
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
        
        # Define your parameters
        daily_limit = 50.0          # Daily spending limit for checking accounts.
        weekly_target = 250.0        # Weekly savings target.
        down_payment_target = 20000.0  # Overall savings goal.
        
        # Calculate progress using your helper function
        progress = calculate_progress_with_accounts(weekly_transactions, daily_limit, weekly_target, account_types, down_payment_target)
        
        # Store the Plaid data (progress, access token, timestamp) under the user's document in Firestore
        db.collection("users").document(uid).set({
            "plaid_progress": progress,
            "plaid_access_token": access_token,
            "last_updated": datetime.now().isoformat()
        }, merge=True)
        
        return JSONResponse(content=progress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def calculate_progress_with_accounts(transactions, daily_limit, weekly_target, account_types, down_payment_target):
    from collections import defaultdict
    daily_spending = defaultdict(float)
    savings_transfers = 0.0
    for txn in transactions:
        account_id = txn.get("account_id")
        subtype = account_types.get(account_id)
        amount = txn.get("amount", 0)
        txn_date = txn.get("date")
        if subtype == "savings":
            if amount > 0:
                savings_transfers += amount
        elif subtype == "checking":
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

@app.post("/api/create_user")
async def create_user(request: CreateUserRequest):
    """
    Creates a new Firebase user with the provided email and password.
    """
    try:
        user = auth.create_user(
            email=request.email,
            password=request.password
        )
        return JSONResponse(content={"uid": user.uid, "email": user.email})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/api/validate_user")
async def validate_user(login: LoginRequest):
    """
    Validates a user's email and password against Firebase Authentication using the REST API.
    Returns the ID token and UID if valid.
    """
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": login.email,
            "password": login.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return JSONResponse(content={
                "idToken": data["idToken"],
                "uid": data["localId"],
                "email": data["email"]
            })
        else:
            raise HTTPException(status_code=400, detail=response.json())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Test writing to Firestore
try:
    doc_ref = db.collection("test").document("connection_check")
    doc_ref.set({"message": "Firebase connected successfully!"})
    print("Data written successfully!")
except Exception as e:
    print(f"Error writing to Firestore: {e}")
