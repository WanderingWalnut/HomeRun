import plaid
import os
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")

def get_transactions():
    # Simulated Plaid API response
    return {"transactions": [{"amount": 50, "category": "Food"}]}
