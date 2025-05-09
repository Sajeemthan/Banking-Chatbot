import re
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb+srv://sr:sr1629@cluster0.nouwfa7.mongodb.net/")
db = client["chatbot"]
faq_collection = db["chatbot"]

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()

        if not user_message:
            return jsonify({"response": "Please enter a message."})

        # Loop through all patterns in DB
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)



