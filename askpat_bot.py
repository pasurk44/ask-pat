
import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY") or "your-secret-key-here"

# Notion database IDs
ASKPAT_DB_ID = "22860630-5b6d-8055-8c5d-c532d55c4e1a"
LOG_DB_ID = "22960630-5b6d-80de-bb33-fd0e62c02389"

# Initialize the Notion client
notion = Client(auth=NOTION_API_KEY)

# Query AskPaT database
try:
    print(f"Querying AskPaT database ID: {ASKPAT_DB_ID}")
    response = notion.databases.query(database_id=ASKPAT_DB_ID)
    print("✅ Success! Fetched AskPaT database:")
    print(response)
except Exception as e:
    print("❌ ERROR querying AskPaT DB:", e)

# (Optional) Test logging to Unanswered DB
try:
    print(f"Logging test question to Log DB: {LOG_DB_ID}")
    response = notion.pages.create(
        parent={ "database_id": LOG_DB_ID },
        properties={
            "Question": {
                "title": [{
                    "text": {
                        "content": "This is a test question log entry"
                    }
                }]
            }
        }
    )
    print("✅ Successfully logged test entry:")
    print(response)
except Exception as e:
    print("❌ ERROR logging to Log DB:", e)
