
import os
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
ASKPAT_DB_ID = os.environ["ASKPAT_DB_ID"]
UNANSWERED_LOG_DB_ID = os.environ["UNANSWERED_LOG_DB_ID"]

notion = Client(auth=NOTION_API_KEY)
app = Flask(__name__)

def query_notion_database(question):
    response = notion.databases.query(database_id=ASKPAT_DB_ID)
    for result in response["results"]:
        props = result["properties"]
        try:
            keywords = props["Topic"]["title"][0]["text"]["content"].lower().split(", ")
            if any(word in question.lower() for word in keywords):
                answer = props["Answer"]["rich_text"][0]["text"]["content"]
                return answer
        except (IndexError, KeyError, TypeError):
            continue
    return None

def log_unanswered_question(question, user=None):
    notion.pages.create(
        parent={"database_id": UNANSWERED_LOG_DB_ID},
        properties={
            "Question": {"title": [{"text": {"content": question}}]},
            "User": {"rich_text": [{"text": {"content": user or "unknown"}}]},
            "Timestamp": {"date": {"start": datetime.utcnow().isoformat()}}
        }
    )

@app.route("/askpat", methods=["POST"])
def askpat():
    user_question = request.form.get("text")
    user_id = request.form.get("user_id")

    answer = query_notion_database(user_question)

   if answer:
    message = f"You asked: *{user_question}*\n\n{answer}"
else:
    message = f"You asked: *{user_question}*\n\nSorry, I don't know the answer yet. I've logged your question!"
    log_unanswered_question(user_question)

return jsonify({"response_type": "ephemeral", "text": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
