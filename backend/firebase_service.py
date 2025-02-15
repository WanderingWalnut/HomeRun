import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("path/to/your/firebase-service-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_data(data):
    db.collection("transactions").add(data)
