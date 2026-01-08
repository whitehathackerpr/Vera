from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins

# Basic conversational memory (for demonstration)
conversation_history = []

@app.route('/ask', methods=['POST'])
def ask_vera():
    data = request.get_json()
    message = data.get('message', '').lower()

    # Add user message to history
    conversation_history.append(f"User: {message}")

    # --- Simple Keyword-Based Logic (for demonstration) ---
    if "hello" in message or "hi" in message:
        reply = "Hello there! How can I help you today?"
    elif "how are you" in message:
        reply = "I'm doing great, thank you for asking! Ready to tackle some work."
    elif "your name" in message:
        reply = "I'm Vera, your AI assistant."
    elif "help" in message:
        reply = "Of course. I can help you with coding questions, generating text, brainstorming ideas, and much more. Just ask!"
    else:
        # A generic reply if no keywords are matched
        reply = f"You said: \"{message}\". I'm still under development, but I'm learning!"
    # -----------------------------------------------------

    # Add Vera's reply to history
    conversation_history.append(f"Vera: {reply}")

    # Keep history from growing too large
    if len(conversation_history) > 10:
        conversation_history.pop(0)

    return jsonify({'reply': reply})

if __name__ == '__main__':
    # Note: In a production environment, you would use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5000) # Use a different port than the frontend
