import firebase_admin
from firebase_admin import credentials, firestore  # Use firestore if you're using Firestore
import os

# Path to the credentials.json file
cred_path = os.path.join(os.path.dirname(__file__), "credentials.json")

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Initialize Firestore database (if using Firestore)
db = firestore.client()

print("Firebase connection successful!")
