import os
import requests
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# Notion setup
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
ASKPAT_DB_ID = os.getenv("ASKPAT_DB_ID")
UNANSWERED_DB_ID = os.getenv("UNANSWERED_DB_ID")
notion = Client(auth=NOTION_API_KEY)

# Helper to format Notion DB ID
def format_notion_id(raw_id):
    raw_id = raw_id.replace("-", "")
    return f"{raw_id[0:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:32]}"

# Get all pages in a Notion DB
def get_database_pages(database_id):
    formatted_id = format_notion_id(database_id)
    response = notion.databases.query(database_id=formatted_id)
    return response.get("results", [])

# Search for matching topic in Notion pages
def search_answer(query, pages):
    query_lower = query.lower()
    for page in pages:
        try:
            topic = page['properties']['Topic']['title'][0]['plain_text'].lower()
            if topic in query_lower:
                answer_blocks = page['properties']['Answer']['rich_text']
                return answer_blocks[0]['plain_text'] if answer_blocks else None
        except (KeyError, IndexError):
            continue
    return None

# Log unanswered question
def log_unanswered_question(query):
    try:
        formatted_id = format_notion_id(UNANSWERED_DB_ID)
        notion.pages.create(
            parent={"database_id": formatted_id},
            properties={
                "Question": {
                    "title": [
                        {
                            "text": {
                                "content": query
                            }
                        }
                    ]
                }
            }
        )
        print(f"📝 Logged unanswered question: {query}")
    except Exception as e:
        print(f"⚠️ Failed to log unanswered question: {e}")

# Slack endpoint
@app.route("/askpat", methods=["POST"])
def askpat():
    try:
        data = request.form
        print(f"📥 Raw request.form: {data}")

        text = data.get("text", "")
        user_id = data.get("user_id", "")

        print(f"🔎 Query from {user_id}: {text}")

        pages = get_database_pages(ASKPAT_DB_ID)
        answer = search_answer(text, pages)

        if answer:
            return jsonify({
                "response_type": "in_channel",
                "text": f"🧠 {answer}"
            })

        log_unanswered_question(text)

        return jsonify({
            "response_type": "ephemeral",
            "text": "🤖 I couldn't find an answer. I've logged this for follow-up!"
        })

    except Exception as e:
        print(f"❌ ERROR in /askpat: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": "Something went wrong. Please try again later."
        }), 200

# Test route
@app.route("/")
def home():
    return "Ask PaT is running!"

# Run the app on 0.0.0.0 for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
