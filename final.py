
import tkinter as tk
from tkinter import scrolledtext
import ollama
import pyttsx3
import speech_recognition as sr
import sqlite3
import threading
import time
import math

# --- 1. INITIALIZE MEMORY (The 'Brain' Storage) ---
conn = sqlite3.connect("vera_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

def save_fact(key, value):
    """Saves a fact (key-value pair) to the database."""
    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_all_facts():
    """Retrieves all facts from the database and formats them into a single string."""
    cursor.execute("SELECT * FROM memory")
    facts = cursor.fetchall()
    return ". ".join([f"The user's {f[0]} is {f[1]}" for f in facts])

# --- 2. INITIALIZE VOICE (The 'Mouth') ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 175)

is_speaking = False

def speak(text):
    """Makes Vera speak the given text. This function runs in a background thread."""
    global is_speaking
    # Schedule the GUI update and set the speaking flag
    def pre_speak_update():
        global is_speaking
        is_speaking = True
        app.update_conversation("Vera", text)
    app.root.after(0, pre_speak_update)

    engine.say(text)
    engine.runAndWait()

    # Schedule setting the speaking flag to false after speaking
    def post_speak_update():
        global is_speaking
        is_speaking = False
    app.root.after(0, post_speak_update)

# --- 3. SPEECH RECOGNITION (The 'Ears') ---
def listen():
    """Listens for user input via the microphone and transcribes it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        app.update_status("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return ""
    try:
        app.update_status("Processing...")
        user_input = r.recognize_google(audio).lower()
        return user_input
    except sr.UnknownValueError:
        app.update_status("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        app.update_status(f"Recognition request failed: {e}")
        return ""

# --- 4. THE PERSONALITY PROMPT ---
def get_vera_response(user_input):
    """Gets a response from the Ollama model based on user input and memory."""
    response = ollama.chat(model='Vera', messages=[
        {'role': 'system', 'content': get_all_facts()},
        {'role': 'user', 'content': user_input},
    ])
    return response['message']['content']

# --- 5. GUI APPLICATION ---
class VeraApp:
    """The main application class for the Tkinter GUI."""
    def __init__(self, root):
        self.root = root
        self.root.title("Vera")
        self.root.configure(bg='#2c2f33')

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='#23272a', fg='#ffffff', font=("Helvetica Neue", 12), state='disabled', padx=10, pady=10)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(root, bg='#2c2f33')
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.entry_box = tk.Entry(self.input_frame, bg='#40444b', fg='#ffffff', font=("Helvetica Neue", 12), insertbackground='white')
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.entry_box.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg='#7289da', fg='white', font=("Helvetica Neue", 10, "bold"), borderwidth=0)
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))

        self.status_label = tk.Label(root, text="Press the button to speak or type a message.", bg='#2c2f33', fg='#99aab5', font=("Helvetica Neue", 10))
        self.status_label.pack(pady=(0, 5))

        self.canvas = tk.Canvas(root, width=300, height=100, bg='#2c2f33', highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.start_animation()
        
        self.root.after(1000, self.start_listening_thread)

    def start_listening_thread(self):
        """Starts the background thread that listens for the 'Vera' hotword."""
        thread = threading.Thread(target=self.run_vera_logic)
        thread.daemon = True
        thread.start()

    def send_message(self, event=None):
        """Handles sending a typed message."""
        user_input = self.entry_box.get()
        if user_input:
            self.entry_box.delete(0, tk.END)
            self.update_conversation("You", user_input)
            self.process_input(user_input)
            
    def process_input(self, user_input):
        """Processes user input, whether from voice or text."""
        if "my name is" in user_input:
            name = user_input.split("is")[-1].strip()
            save_fact("name", name)
            speak_thread = threading.Thread(target=speak, args=(f"Got it, I'll never forget that your name is {name}.",))
            speak_thread.start()
        else:
            def respond():
                reply = get_vera_response(user_input)
                speak(reply)
            respond_thread = threading.Thread(target=respond)
            respond_thread.start()

    def update_conversation(self, sender, message):
        """Appends a message to the chat area in a thread-safe way."""
        def _update():
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
            self.chat_area.config(state='disabled')
            self.chat_area.yview(tk.END)
        self.root.after(0, _update)

    def update_status(self, text):
        """Updates the status label at the bottom of the GUI in a thread-safe way."""
        def _update():
            self.status_label.config(text=text)
        self.root.after(0, _update)

    def start_animation(self):
        """Initializes the voice animation."""
        self.animating = True
        self.angle = 0
        self.animate()

    def animate(self):
        """The main animation loop. Redraws the canvas periodically."""
        if not self.animating: return
            
        self.canvas.delete("all")
        if is_speaking:
            num_bars = 10
            max_height = 50
            for i in range(num_bars):
                angle_offset = self.angle + i * (360 / num_bars)
                height = max_height / 2 * (1 + math.sin(math.radians(angle_offset * 4 + self.angle * 2)))
                x0 = i * 30
                y0 = 50 - height / 2
                x1 = (i + 1) * 30 - 5
                y1 = 50 + height / 2
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='#7289da', outline="")
            self.angle += 5
        else:
             self.canvas.create_line(10, 50, 290, 50, fill='#40444b', width=2)

        self.root.after(30, self.animate)

    def run_vera_logic(self):
        """The main loop that continuously listens for the hotword."""
        self.update_status("Vera is ready.")
        while True:
            command = listen()
            if command and "vera" in command:
                # Update GUI in main thread
                self.root.after(0, self.update_conversation, "You", command)
                self.process_input(command.replace("vera", "").strip())
            time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = VeraApp(root)
    root.mainloop()
