
import os
from flask import Flask, request, jsonify
from notion_client import Client
from dotenv import load_dotenv
import re

load_dotenv()

# Initialize Notion client and Flask app
notion = Client(auth=os.environ["NOTION_API_KEY"])
ASKPAT_DB_ID = os.environ["ASKPAT_DB_ID"]
UNANSWER_DB_ID = os.environ["UNANSWER_DB_ID"]

app = Flask(__name__)

# 🧠 Utility: Clean and normalize user query
def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

# 🔍 Search Notion for answer
def search_answer(query, pages):
    norm_query = normalize(query)

    for page in pages:
        topic_data = page["properties"].get("Topic", {}).get("title", [])
        answer_data = page["properties"].get("Answer", {}).get("rich_text", [])

        if not topic_data or not answer_data:
            continue

        topic = topic_data[0]["plain_text"].lower()
        keywords = [normalize(word) for word in topic.split(",")]

        if any(word in norm_query for word in keywords):
            answer_parts = [part.get("plain_text", "") for part in answer_data]
            return "".join(answer_parts)

    return None

# 🗃 Get database pages
def get_pages():
    pages = []
    next_cursor = None

    while True:
        response = notion.databases.query(
            **({"database_id": ASKPAT_DB_ID, "start_cursor": next_cursor} if next_cursor else {"database_id": ASKPAT_DB_ID})
        )
        pages.extend(response["results"])
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break

    return pages

# 📝 Log unanswered questions
def log_unanswered_question(query):
    notion.pages.create(
        parent={"database_id": UNANSWER_DB_ID},
        properties={
            "Question": {
                "title": [{"text": {"content": query}}]
            }
        }
    )

# 📬 Slack slash command endpoint
@app.route("/askpat", methods=["POST"])
def askpat():
    text = request.form.get("text", "")
    if not text:
        return jsonify(response_type="ephemeral", text="Please provide a question after /askpat.")

    try:
        pages = get_pages()
        answer = search_answer(text, pages)

        if answer:
            return jsonify(response_type="in_channel", text=answer)
        else:
            log_unanswered_question(text)
            return jsonify(response_type="in_channel", text="Sorry, I don't know the answer yet. I've logged your question!")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(response_type="ephemeral", text="Something went wrong. Please try again later.")

# 🛠 Default route
@app.route("/")
def home():
    return "Ask PaT is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
