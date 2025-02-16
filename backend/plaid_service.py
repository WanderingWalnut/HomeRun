import os
from plaid import ApiClient, Configuration
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from the specified .env file path
env_path = "/Users/naveed/HomeRun/frontend/frontend/.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from: {env_path}")
else:
    print(f"❌ Error: .env file not found at {env_path}")
    exit(1)

# Load necessary environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "your-client-id")
PLAID_SECRET = os.getenv("PLAID_SECRET", "your-sandbox-secret")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")  # Change to "production" if needed

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    print("❌ Error: Missing Plaid credentials!")
    exit(1)
else:
    print("✅ Plaid credentials loaded successfully!")

# Configure Plaid API Client
host = "https://sandbox.plaid.com"
if PLAID_ENV == "production":
    host = "https://production.plaid.com"  # Adjust accordingly for production

configuration = Configuration(
    host=host,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)

# Create the API client and Plaid API instance
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def fetch_transactions(access_token):
    """Fetches recent transactions from Plaid for the last 30 days."""
    try:
        # Set the date range
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()

        # Log the access token for debugging purposes
        print(f"🔍 Debug: Access Token -> {access_token}")

        # Check if the access token appears valid
        if not access_token.startswith("access-"):
            print("❌ Error: Invalid access token format!")
            return None

        # Build the request object
        request_body = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )

        # Call the Plaid API to get transactions
        response = plaid_client.transactions_get(request_body)
        transactions = response.to_dict().get("transactions", [])
        return transactions

    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")
        return None

print("✅ Plaid API successfully initialized!")
