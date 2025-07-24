import os
import re
import requests
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# 🔐 Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
QA_DATABASE_ID = "228606305b6d80558c5dc532d55c4e1a"  # AskPaT DB
UNANSWERED_LOG_ID = "229606305b6d80debb33fd0e62c02389"  # Log DB

# ⚙️ Format Notion UUID (dash-inserted 32-char)
def format_notion_id(raw_id):
    raw_id = raw_id.replace("-", "")
    return f"{raw_id[0:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:32]}"

# 🧠 Extract text from Slack slash command payload
def extract_text(payload):
    text = payload.get('text', '').strip()
    return re.sub(r'[^a-zA-Z0-9\s\-,.?!]', '', text)

# 🔍 Match question to topic in Notion DB
def search_answer(question, pages):
    question_lower = question.lower()

    for page in pages:
        try:
            title_list = page['properties']['Topic']['title']
            if not title_list:
                print(f"⚠️ Skipped page with empty Topic: {page.get('id')}")
                continue

            topic = title_list[0]['plain_text'].lower()
            if topic in question_lower:
                answer_parts = page['properties']['Answer']['rich_text']
                answer = ''.join([part['plain_text'] for part in answer_parts])
                return answer.strip()
        except KeyError as e:
            print(f"⚠️ Missing expected property in page {page.get('id')}: {e}")
            continue

    return None

# 📝 Log unanswered questions to Notion
def log_unanswered_question(notion, question):
    notion.pages.create(
        parent={"database_id": format_notion_id(UNANSWERED_LOG_ID)},
        properties={
            "Question": {"title": [{"text": {"content": question}}]},
            "Answered": {"checkbox": False}
        }
    )

# 🚀 Flask app and /askpat route
app = Flask(__name__)
notion = Client(auth=NOTION_API_KEY)

@app.route("/askpat", methods=["POST"])
def askpat():
    payload = request.form
    question = extract_text(payload)

    try:
        db_id = format_notion_id(QA_DATABASE_ID)
        pages = notion.databases.query(database_id=db_id).get('results', [])
        answer = search_answer(question, pages)

        if answer:
            return jsonify({"response_type": "in_channel", "text": answer})
        else:
            log_unanswered_question(notion, question)
            return jsonify({"response_type": "ephemeral", "text": "🤔 I don't have an answer for that yet. I'll pass it on to the team!"})
    except Exception as e:
        print("❌ ERROR in /askpat:", e)
        return jsonify({"response_type": "ephemeral", "text": "Something went wrong. Please try again later."})

# 🔧 Default route (optional for testing)
@app.route("/")
def home():
    return "Ask PaT is running!"

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


