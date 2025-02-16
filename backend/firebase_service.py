import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

try:
    logging.debug("Starting Firebase initialization...")

    # Specify the path to credentials.json
    cred_path = "/Users/naveed/HomeRun/backend/credentials.json"

    # Check if credentials.json exists
    if not os.path.exists(cred_path):
        logging.error(f"Credentials file not found: {cred_path}")
        raise FileNotFoundError("Firebase credentials file not found!")

    logging.debug(f"Using credentials file at: {cred_path}")

    # Prevent multiple Firebase initializations
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logging.debug("Firebase initialized successfully!")
    else:
        logging.debug("Firebase already initialized, skipping reinitialization.")

    # Initialize Firestore
    db = firestore.client()
    logging.debug("Firestore database connection established!")

    print("✅ Firebase connection successful!")

except Exception as e:
    logging.error(f"🔥 Error initializing Firebase: {e}", exc_info=True)
