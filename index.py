import re
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import spacy
nlp = spacy.load("en_core_web_sm")  # Load spaCy NLP model


app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["chatbot"]
faq_collection = db["chatbot"]

intents = {
    "check_balance": ["balance", "account balance", "how much money", "available funds"],
    "transfer_money": ["transfer", "send money", "move money", "pay"],
    "open_account": ["open account", "create account", "new account"],
    "loan_inquiry": ["loan", "borrow", "apply loan", "loan interest"],
    "card_issue": ["card", "lost card", "block card", "credit card", "debit card"]
}

intent_responses = {
    "check_balance": "You can check your balance via the mobile app or ATM.",
    "transfer_money": "To transfer money, go to the Transfers section and follow the steps.",
    "open_account": "You can open a new account online or visit a nearby branch.",
    "loan_inquiry": "We offer personal, home, and auto loans. Want to apply?",
    "card_issue": "For card issues, please call our 24/7 helpline or block via the app."
}

def classify_intent(user_input):
    doc = nlp(user_input.lower())
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input.lower():
                return intent
    return "unknown"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()

        if not user_message:
            return jsonify({"response": "Please enter a message."})

        # 🔍 First: Try NLP intent classification
        intent = classify_intent(user_message)
        if intent in intent_responses:
            return jsonify({"response": intent_responses[intent]})

        # 🧠 If NLP fails: Try regex-based MongoDB FAQ
        for doc in faq_collection.find():
            pattern = doc.get("pattern", "")
            if re.search(pattern, user_message):
                responses = doc.get("responses", [])
                if responses:
                    return jsonify({"response": random.choice(responses)})
                else:
                    return jsonify({"response": "Sorry, I found a match but no response is defined."})

        return jsonify({"response": "Sorry, I couldn't find an answer to your question."})

    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"})


# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         user_message = data.get('message', '').lower()

#         if not user_message:
#             return jsonify({"response": "Please enter a message."})

#         # Loop through all patterns in DB
#         for doc in faq_collection.find():
#             pattern = doc.get("pattern", "")
#             if re.search(pattern, user_message):
#                 responses = doc.get("responses", [])
#                 if responses:
#                     return jsonify({"response": random.choice(responses)})
#                 else:
#                     return jsonify({"response": "Sorry, I found a match but no response is defined."})

#         return jsonify({"response": "Sorry, I couldn't find an answer to your question."})

#     except Exception as e:
#         return jsonify({"response": f"An error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)



