
import ollama
import pyttsx3
import speech_recognition as sr
import sqlite3
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1. INITIALIZE MEMORY (The 'Brain' Storage) ---
conn = sqlite3.connect("vera_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

def save_fact(key, value):
    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_all_facts():
    cursor.execute("SELECT * FROM memory")
    facts = cursor.fetchall()
    return ". ".join([f"The user's {f[0]} is {f[1]}" for f in facts])

# --- 2. THE PERSONALITY PROMPT ---
def get_vera_response(user_input):
    history = get_all_facts()
    
    response = ollama.chat(model='Vera', messages=[
        {'role': 'user', 'content': user_input},
    ])
    return response['message']['content']

# --- 3. FLASK SERVER ---
app = Flask(__name__)
CORS(app)

@app.route("/ask", methods=['POST'])
def ask_vera():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    if "my name is" in user_input:
        name = user_input.split("is")[-1].strip()
        save_fact("name", name)
        reply = f"Got it, I'll never forget that your name is {name}."
    else:
        reply = get_vera_response(user_input)
        
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000)
