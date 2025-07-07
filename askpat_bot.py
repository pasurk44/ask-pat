from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os
from datetime import datetime
from notion_client import Client

# Slack + Notion setup
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
notion = Client(auth=os.environ.get("NOTION_API_KEY"))
LOG_DB_ID = "229606305b6d80cfb5b4f9f761607f87"  # Unanswered questions DB

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

def log_unanswered_question(query, user_id):
    now = datetime.utcnow().isoformat()
    try:
        notion.pages.create(parent={"database_id": LOG_DB_ID}, properties={
            "Query": {
                "title": [{"text": {"content": query}}]
            },
            "User": {
                "rich_text": [{"text": {"content": user_id}}]
            },
            "Date": {
                "date": {"start": now}
            }
        })
    except Exception as e:
        print(f"[Logging Error] {e}")

@app.command("/askpat")
def handle_askpat(ack, respond, command):
    ack()
    user_input = command["text"]
    user_id = command["user_id"]
    answer = None  # TEMP: skip Notion DB query

    if answer:
        respond(answer)
    else:
        log_unanswered_question(user_input, user_id)
        respond(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"> 🤷‍♂️ I couldn’t find an answer for: *{user_input}*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📂 Open People Team Notion"},
                            "url": "https://www.notion.so/teammetronome/People-and-Talent-174606305b6d80a497e9c1e0e31fea0b"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✉️ Email HR"},
                            "url": "mailto:hr@metronome.com"
                        }
                    ]
                }
            ]
        )

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)
