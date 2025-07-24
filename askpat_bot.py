import os
from flask import Flask, request, jsonify
from notion_client import Client
import requests

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_API_KEY"])
ASKPAT_DB_ID = os.environ["ASKPAT_DB_ID"]
UNANSWERED_LOG_DB_ID = os.environ["UNANSWERED_LOG_DB_ID"]

# Initialize Slack credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

app = Flask(__name__)

def query_notion_database(query):
    response = notion.databases.query(
        **{
            "database_id": ASKPAT_DB_ID,
        }
    )
    query = query.lower()
    for result in response.get("results", []):
        props = result["properties"]
        keywords = props["Topic"]["title"][0]["text"]["content"].lower().split(", ")
        answer = props["Answer"]["rich_text"][0]["text"]["content"]
        if any(word in query for word in keywords):
            return answer
    return None

def log_unanswered_question(question):
    notion.pages.create(
        **{
            "parent": {"database_id": UNANSWERED_LOG_DB_ID},
            "properties": {
                "Question": {
                    "title": [{"text": {"content": question}}]
                }
            },
        }
    )

@app.route("/askpat", methods=["POST"])
def askpat():
    data = request.form
    user_question = data.get("text", "")
    channel_id = data.get("channel_id")
    response_url = data.get("response_url")

    answer = query_notion_database(user_question)
    if answer:
        requests.post(response_url, json={"text": answer})
    else:
        log_unanswered_question(user_question)
        requests.post(response_url, json={"text": "Sorry, I don't know the answer yet. I've logged your question!"})
    return "", 200

@app.route("/")
def home():
    return "Ask PaT is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
