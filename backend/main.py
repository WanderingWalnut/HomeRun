from fastapi import FastAPI
from plaid_service import plaid_client  # Import plaid_client from plaid_service
from plaid_service import fetch_transactions  # Import fetch_transactions from plaid_service
from firebase_service import db  # Import db from firebase_service
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from flask import request
from flask import jsonify


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hackathon API is running!"}

@app.route("/api/exchange_public_token", methods=["POST"])
def exchange_public_token():
    """Exchanges a public token for an access token."""
    try:
        data = request.json
        public_token = data.get("public_token")

        if not public_token:
            return jsonify({"error": "Public token is required"}), 400

        request_body = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request_body)

        # Extract the access token
        access_token = response["access_token"]
        item_id = response["item_id"]

        # 🚨 Store access_token securely (e.g., database)
        print(f"Access Token: {access_token}, Item ID: {item_id}")

        return jsonify({"access_token": access_token, "item_id": item_id})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/get_transactions", methods=["POST"])
def get_transactions():
    """Fetches and processes user transactions."""
    try:
        data = request.json
        access_token = data.get("access_token")

        if not access_token:
            return jsonify({"error": "Access token is required"}), 400

        transactions = fetch_transactions(access_token)

        if transactions is None:
            return jsonify({"error": "Failed to fetch transactions"}), 500

        # Separate transactions: Spending vs. Savings Transfers
        spending_transactions = []
        savings_transfers = []

        for txn in transactions:
            if "transfer" in txn["category"]:  # Identifying savings transfers
                savings_transfers.append(txn)
            else:
                spending_transactions.append(txn)

        return jsonify({
            "spending_transactions": spending_transactions,
            "savings_transfers": savings_transfers
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Test writing to Firestore
doc_ref = db.collection("test").document("connection_check")
doc_ref.set({"message": "Firebase connected successfully!"})

print("Data written successfully!")

