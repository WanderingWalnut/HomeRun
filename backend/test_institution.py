from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

# Step 1: Generate a Sandbox Public Token
request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109511",  # Fake test bank
    initial_products=["transactions"]
)
response = client.sandbox_public_token_create(request)
public_token = response["public_token"]

# Step 2: Exchange Public Token for Access Token
exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
exchange_response = client.item_public_token_exchange(exchange_request)
ACCESS_TOKEN = exchange_response["access_token"]

print("✅ Sandbox Access Token:", ACCESS_TOKEN)
