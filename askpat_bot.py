import os
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv
import requests

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
ASKPAT_DB_ID = os.environ["ASKPAT_DB_ID"]
UNANSWERED_LOG_DB_ID = os.environ["UNANSWERED_LOG_DB_ID"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = Flask(__name__)

def query_notion_database(user_question):
    response = notion.databases.query(database_id=ASKPAT_DB_ID)
    for result in response.get("results", []):
        props = result["properties"]
        try:
            keywords = props["Topic"]["title"][0]["text"]["content"].lower().split(", ")
            answer = props["Answer"]["rich_text"][0]["text"]["content"]
            for word in keywords:
                if word in user_question.lower():
                    return answer
        except (KeyError, IndexError):
            continue
    return None

def log_unanswered_question(question):
    notion.pages.create(
        parent={"database_id": UNANSWER_DB_ID},
        properties={"Name": {"title": [{"text": {"content": question}}]}}
    )

def post_to_slack_channel(channel_id, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel_id,
        "text": text
    }
    requests.post(url, headers=headers, json=payload)

@app.route("/askpat", methods=["POST"])
def askpat():
    user_question = request.form.get("text")
    channel_id = request.form.get("channel_id")
    is_private = channel_id.startswith("D")

    answer = query_notion_database(user_question)

    if not is_private:
        post_to_slack_channel(channel_id, f"_<@{request.form.get('user_id')}> asked:_ {user_question}")

    if answer:
        message = answer
    else:
        message = "Sorry, I don't know the answer yet. I've logged your question!"
        log_unanswered_question(user_question)

    return jsonify({"response_type": "in_channel", "text": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
