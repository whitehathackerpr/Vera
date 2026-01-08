import ollama
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1. INITIALIZE MEMORY (The '''Brain''' Storage) ---
# Use a file for the database so memory persists across restarts
DB_FILE = "vera_memory.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

def save_fact(key, value):
    """Saves a key-value fact to the database."""
    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_all_facts():
    """Retrieves all facts from the database and formats them into a string."""
    cursor.execute("SELECT key, value FROM memory")
    facts = cursor.fetchall()
    if not facts:
        return "You don't have any saved facts about the user yet."
    return ". ".join([f"The user's {f[0]} is {f[1]}" for f in facts])

# --- 2. THE OLLAMA INTEGRATION ---
def get_vera_response(user_input):
    """Gets a response from the Ollama model, including user facts as context."""
    known_facts = get_all_facts()
    
    # The system prompt provides context and personality for the model.
    system_prompt = (
        "You are Vera, a friendly and highly capable AI assistant integrated into a development environment. "
        "Your responses should be conversational, helpful, and concise. "
        f"Here is some information you have stored about the user: {known_facts}"
    )

    try:
        # Use the 'vera' model as requested in your logic
        response = ollama.chat(model='vera', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']
    except Exception as e:
        # Handle cases where the ollama service might not be running
        print(f"Error contacting Ollama: {e}")
        return "I'm having trouble connecting to my core intelligence. Please make sure the Ollama service is running."


# --- 3. FLASK SERVER ---
app = Flask(__name__)
CORS(app)  # Allow all origins for development

@app.route("/ask", methods=['POST'])
def ask_vera_endpoint():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Simple hardcoded rule for memory as in your example
    if "my name is" in user_input.lower():
        # Extracts the name after "is". This is a simple parser.
        name = user_input.lower().split("my name is")[-1].strip().title()
        save_fact("name", name)
        reply = f"Got it. I'll remember that your name is {name}."
    else:
        # For all other inputs, query the generative model
        reply = get_vera_response(user_input)
        
    return jsonify({"reply": reply})

if __name__ == "__main__":
    # In a production environment, use a proper WSGI server like Gunicorn.
    # The host must be 0.0.0.0 to be accessible from other containers.
    app.run(host='0.0.0.0', port=5000, debug=True)
