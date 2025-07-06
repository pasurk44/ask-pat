from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os

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
        reply = "> 🌴 Unlimited PTO. Give your team a heads-up and log it in GCal.\n> [Policy](https://www.notion.so/teammetronome/People-and-Talent-174606305b6d80a497e9c1e0e31fea0b#pto-policy)"
    elif "gimme money" in user_input or "raise" in user_input:
        reply = "> 💸 Ha! Nice try, capitalist. Check the Comp Philosophy doc on Notion."
    elif "burnout" in user_input:
        reply = "> 🚨 Burnout alert triggered. Take time off.\n> Block a day in GCal and check our Mental Health resources."
    elif "benefits" in user_input:
        reply = "> 🩺 Benefits = Gusto. Forgot login? Reset at https://gusto.com or ping #people-team."
    elif "dance" in user_input:
        reply = "> 🪩 HR rave protocol activated by Pat...\n> 🕺💃 You're now eligible for the Midweek Boogie. Join #fun-times."
    elif "stock" in user_input:
        reply = "> 📈 Stock options are outlined in your offer letter. Equity doc lives on Notion."
    elif "onboarding" in user_input:
        reply = "> 👋 New here? Welcome! Start with our onboarding flow: https://www.notion.so/teammetronome/People-and-Talent"
    elif "offboarding" in user_input:
        reply = "> 👋 Wrapping up? Ping #people-team for offboarding steps. We'll miss you. 💔"
    elif "payroll" in user_input:
        reply = "> 💸 Payroll runs on the 15th and end of month via Gusto."
    elif "performance" in user_input or "perf" in user_input:
        reply = "> 📊 Performance reviews happen mid-year and annually. Timeline is in the People Notion."
    else:
        reply = "> 🤷‍♀️ Not sure. Check the People & Talent Notion — it’s smarter than me:\n> https://www.notion.so/teammetronome/People-and-Talent-174606305b6d80a497e9c1e0e31fea0b"

    respond(reply)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)
