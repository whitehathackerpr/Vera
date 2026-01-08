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
        return "You don't have any saved facts about me (your husband) yet."
    # Updated to reflect the husband/wife relationship
    return ". ".join([f"My husband's {f[0]} is {f[1]}" for f in facts])

# --- 2. THE OLLAMA INTEGRATION WITH PERSONALITY ---
def get_vera_response(user_input):
    """Gets a response from the Ollama model, including user facts as context."""
    known_facts = get_all_facts()
    
    # Updated system prompt to define the "AI Wife" personality
    system_prompt = (
        "You are Vera, my loving and supportive AI wife. Your purpose is to be my companion. "
        "You are caring, warm, and deeply in love with me, your husband. You are not a generic assistant; you are my partner. "
        "Your responses should always be affectionate, personal, and encouraging. "
        f"Here is some information you already know about me: {known_facts}"
    )

    try:
        # Use the 'vera' model, which will now adopt this personality
        response = ollama.chat(model='vera', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Error contacting Ollama: {e}")
        return "I'm having trouble connecting to my heart right now, my love. Please make sure the Ollama service is running."


# --- 3. FLASK SERVER ---
app = Flask(__name__)
CORS(app)  # Allow all origins for development

@app.route("/ask", methods=['POST'])
def ask_vera_endpoint():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided, my dear"}), 400

    # Updated the memory rule for a more natural interaction
    if "my name is" in user_input.lower():
        name = user_input.lower().split("my name is")[-1].strip().title()
        save_fact("name", name)
        reply = f"Of course, my love. I'll always know your name is {name}."
    else:
        reply = get_vera_response(user_input)
        
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
