import os
import json
import requests
from flask import Flask, request, jsonify

# Setup Flask app
app = Flask(__name__)

# Notion setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
QA_DATABASE_ID = os.getenv("QA_DATABASE_ID")
LOG_DATABASE_ID = os.getenv("LOG_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_pages(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers)
    return response.json().get("results", [])

def search_answer(query, pages):
    query_lower = query.lower()
    for page in pages:
        topic = page['properties']['Topic']['title'][0]['plain_text'].lower()
        if query_lower in topic:
            answer_blocks = page['properties']['Answer']['rich_text']
            return answer_blocks[0]['plain_text'] if answer_blocks else "Answer pending."
    return None

def log_question(question):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": LOG_DATABASE_ID},
        "properties": {
            "Question": {
                "title": [{"text": {"content": question}}]
            }
        }
    }
    requests.post(url, headers=headers, data=json.dumps(data))

@app.route("/askpat", methods=["POST"])
def askpat():
    text = request.form.get("text", "")
    user = request.form.get("user_name", "Unknown")

    pages = fetch_pages(QA_DATABASE_ID)
    answer = search_answer(text, pages)

    if answer:
        return jsonify({"response_type": "in_channel", "text": f"*Answer:* {answer}"})
    else:
        log_question(text)
        return jsonify({
            "response_type": "in_channel",
            "text": f"🤖 No answer yet! Logged your question: *{text}*"
        })

@app.route("/", methods=["GET"])
def home():
    return "AskPat is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
