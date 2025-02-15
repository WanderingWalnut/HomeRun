from fastapi import FastAPI
from plaid_service import get_transactions
from firebase_service import save_data

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hackathon API is running!"}

@app.get("/transactions")
def transactions():
    data = get_transactions()
    save_data(data)
    return {"status": "Saved to Firebase", "data": data}
