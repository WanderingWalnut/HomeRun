import os
from plaid import ApiClient, Configuration, ApiException
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser

from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta


# Load environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")  # Use "development" or "production" if needed

# Configure Plaid API Client
configuration = Configuration(
    host="https://sandbox.plaid.com",  # Change for production
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)

api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def fetch_transactions(access_token):
    """Fetches recent transactions from Plaid."""
    try:
        # Set date range (last 30 days)
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        request_body = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )

        response = plaid_client.transactions_get(request_body)
        transactions = response["transactions"]

        return transactions  # Return transactions for further processing

    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return None

print("Plaid API successfully initialized!")
