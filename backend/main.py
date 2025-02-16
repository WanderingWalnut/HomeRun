from fastapi import FastAPI
from plaid_service import get_transactions
from firebase_service import db  # Import db from firebase_service

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hackathon API is running!"}


# Test writing to Firestore
doc_ref = db.collection("test").document("connection_check")
doc_ref.set({"message": "Firebase connected successfully!"})

print("Data written successfully!")

