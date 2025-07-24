import os
import requests
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

notion = Client(auth=os.environ["NOTION_API_KEY"])
ASKPAT_DB_ID = os.environ["ASKPAT_DB_ID"]
UNANSWERED_LOG_DB_ID = os.environ["UNANSWERED_LOG_DB_ID"]

def search_answer(user_input, pages):
    user_input_lower = user_input.lower()

    for page in pages:
        try:
            topic_property = page['properties']['Topic']['title']
            if not topic_property:
                continue
            topic_text = topic_property[0]['plain_text'].lower()
            keywords = [k.strip() for k in topic_text.split(",")]

            for keyword in keywords:
                if keyword in user_input_lower:
                    answer_property = page['properties'].get('Answer', {}).get('rich_text', [])
                    if answer_property:
                        return answer_property[0]['plain_text']
        except (KeyError, IndexError):
            continue

    return None

@app.route("/askpat", methods=["POST"])
def askpat():
    try:
        text = request.form.get("text", "").strip()
        print(f"📨 Received question: {text}")

        if not text:
            return jsonify({"response_type": "ephemeral", "text": "Please enter a question."})

        db_response = notion.databases.query(database_id=ASKPAT_DB_ID)
        pages = db_response.get("results", [])
        print(f"📄 Fetched {len(pages)} pages from AskPaT DB")

        answer = search_answer(text, pages)

        if answer:
            return jsonify({"response_type": "in_channel", "text": answer})
        else:
            notion.pages.create(
                parent={"database_id": UNANSWERED_LOG_DB_ID},
                properties={
                    "Question": {
                        "title": [
                            {
                                "text": {
                                    "content": text
                                }
                            }
                        ]
                    }
                }
            )
            print("📭 No match found — logged unanswered question.")
            return jsonify({"response_type": "in_channel", "text": "Sorry, I don't know the answer yet. I've logged your question!"})

    except Exception as e:
        print(f"🔥 Exception occurred: {e}")
        return jsonify({"response_type": "ephemeral", "text": f"Something went wrong: {str(e)}"})

@app.route("/")
def home():
    return "Ask PaT is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
