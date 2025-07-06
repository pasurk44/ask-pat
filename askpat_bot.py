from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@app.command("/askpat")
def handle_askpat(ack, respond, command):
    ack()
    user_input = command["text"].lower()
    print(f"Received command: {user_input}")

    if "time off" in user_input:
        reply = "> 🌴 Unlimited PTO, but don’t ghost. Give your team a heads-up and log it in GCal.\n> Details: https://www.notion.so/teammetronome/People-and-Talent-174606305b6d80a497e9c1e0e31fea0b#pto-policy"
    elif "gimme money" in user_input:
        reply = "> 💸 Ha! Nice try, capitalist. Talk to your manager and check the Comp Philosophy doc on HR Notion."
    elif "burnout" in user_input:
        reply = "> 🚨 Burnout alert triggered. Grab some time off — seriously.\n> Block a day in GCal and check our Mental Health resources."
    elif "benefits" in user_input:
        reply = "> 🩺 Benefits run through Gusto. Forgot your login? Reset it at https://gusto.com or ping #people-team."
    elif "dance" in user_input:
        reply = "> 🪩 HR rave protocol activated by Pat...\n> 🕺💃 You're now eligible for the Mandatory Midweek Boogie. See #fun-times."
    else:
        reply = "> 🤷‍♀️ No clue. Check the People & Talent Notion — it’s smarter than me:\n> https://www.notion.so/teammetronome/People-and-Talent-174606305b6d80a497e9c1e0e31fea0b"

    respond(reply)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)
