import plaid
import json
from plaid.api import plaid_api
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


# Initialize the Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,  # Change for different environments
    api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)



def get_transactions():
    # Simulated Plaid API response
    return {"transactions": [{"amount": 50, "category": "Food"}]}


# ------------------------------
# 2. Fetch Account Balances
# ------------------------------
def get_balances():
    request = plaid.models.AccountsBalanceGetRequest(access_token=ACCESS_TOKEN)
    response = client.accounts_balance_get(request)
    
    accounts = response["accounts"]
    total_balance = sum(acc["balances"]["current"] for acc in accounts)
    
    print("\n📊 Total Bank Balance:", total_balance)
    for acc in accounts:
        print(f"- {acc['name']}: ${acc['balances']['current']}")

    return accounts, total_balance

# ------------------------------
# 3. Fetch Recent Transactions
# ------------------------------
def get_transactions():
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    request = plaid.models.TransactionsGetRequest(
        access_token=ACCESS_TOKEN,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)
    
    transactions = response["transactions"]
    print("\n📜 Recent Transactions:")
    
    for txn in transactions:
        print(f"- {txn['date']} | {txn['name']} | ${txn['amount']} | Category: {txn.get('category', 'Unknown')}")
    
    return transactions

# ------------------------------
# 4. Detect Savings Transfers or Spending
# ------------------------------
def analyze_transactions(transactions):
    spent_total = 0
    saved_total = 0

    for txn in transactions:
        amount = txn["amount"]
        categories = txn.get("category", [])

        if "Transfer" in categories and "Savings" in categories:
            saved_total += amount
        elif "Payment" in categories or "Food and Drink" in categories:
            spent_total += amount

    print("\n📈 Summary:")
    print(f"- 💰 Total Sent to Savings: ${saved_total}")
    print(f"- 💸 Total Money Spent: ${spent_total}")
