import plaid
import os
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta
from plaid.model.products import Products
from datetime import datetime, timedelta
# Load API credentials from .env file
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = "sandbox"

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise ValueError("❌ Missing Plaid API credentials! Check your .env file.")

# Initialize Plaid Client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_sandbox_access_token():
    """ Generate a Plaid sandbox access token for testing """
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109511",  # Fake Plaid sandbox bank
        initial_products=[Products("transactions")]
    )
    response = client.sandbox_public_token_create(request)
    public_token = response.public_token

    # Exchange public token for access token
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = client.item_public_token_exchange(exchange_request)
    return exchange_response.access_token

def get_balances(access_token):
    """ Retrieve mock bank balances from the sandbox account """
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)

    print("\n📊 Bank Balances:")
    for account in response.accounts:
        print(f" - {account.name}: ${account.balances.current}")

from datetime import date, timedelta

def get_transactions(access_token):
    """ Retrieve example transactions from the sandbox account """
    start_date = date.today() - timedelta(days=30)  # Ensure it's a date object
    end_date = date.today()  # Ensure it's a date object

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)

    print("\n📜 Recent Transactions:")
    for txn in response.transactions:
        print(f"- {txn.date} | {txn.name} | ${txn.amount} | Category: {txn.category}")

if __name__ == "__main__":
    print("🔄 Generating Sandbox Access Token...")
    access_token = create_sandbox_access_token()

    print("\n✅ Sandbox Access Token Generated")
    get_balances(access_token)
    get_transactions(access_token)
