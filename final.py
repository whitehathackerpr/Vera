
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
# Connect to the SQLite database. A new file 'vera_memory.db' will be created if it doesn't exist.
# `check_same_thread=False` allows the database connection to be used from multiple threads.
conn = sqlite3.connect("vera_memory.db", check_same_thread=False)
cursor = conn.cursor()
# Create a 'memory' table if it doesn't already exist. This table will store key-value pairs.
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

def save_fact(key, value):
    """Saves a fact (key-value pair) to the database."""
    # Use INSERT OR REPLACE to either add a new fact or update an existing one.
    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_all_facts():
    """Retrieves all facts from the database and formats them into a single string."""
    cursor.execute("SELECT * FROM memory")
    facts = cursor.fetchall()
    # Format each fact as "The user's [key] is [value]" and join them together.
    return ". ".join([f"The user's {f[0]} is {f[1]}" for f in facts])

# --- 2. INITIALIZE VOICE (The 'Mouth') ---
# Initialize the text-to-speech engine.
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Set the voice to a female voice (index 1). This may vary depending on the system.
engine.setProperty('voice', voices[1].id) 
# Set the speaking rate (words per minute).
engine.setProperty('rate', 175)

# A flag to track if Vera is currently speaking, used for the animation.
is_speaking = False

def speak(text):
    """Makes Vera speak the given text and updates the GUI."""
    global is_speaking
    is_speaking = True
    # Update the conversation display in the GUI.
    app.update_conversation("Vera", text)
    # Use the TTS engine to say the text.
    engine.say(text)
    # Block until speaking is finished.
    engine.runAndWait()
    is_speaking = False

# --- 3. SPEECH RECOGNITION (The 'Ears') ---
def listen():
    """Listens for user input via the microphone and transcribes it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        app.update_status("Listening...")
        # Adjust for ambient noise.
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        # Use Google's speech recognition to convert audio to text.
        user_input = r.recognize_google(audio).lower()
        app.update_status("Processing...")
        return user_input
    except Exception as e:
        # Handle cases where the audio could not be understood.
        app.update_status(f"Could not understand audio: {e}")
        return ""

# --- 4. THE PERSONALITY PROMPT ---
def get_vera_response(user_input):
    """Gets a response from the Ollama model based on user input and memory."""
    # This function now only sends the user input, as the personality is defined in the model file.
    response = ollama.chat(model='Vera', messages=[
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

        # ScrolledText widget for displaying the chat history.
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='#23272a', fg='#ffffff', font=("Helvetica Neue", 12), state='disabled', padx=10, pady=10)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Frame to hold the entry box and send button.
        self.input_frame = tk.Frame(root, bg='#2c2f33')
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Entry widget for typing messages.
        self.entry_box = tk.Entry(self.input_frame, bg='#40444b', fg='#ffffff', font=("Helvetica Neue", 12), insertbackground='white')
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.entry_box.bind("<Return>", self.send_message) # Bind Enter key to send message.

        # Button to send the message.
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg='#7289da', fg='white', font=("Helvetica Neue", 10, "bold"), borderwidth=0)
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Label to show Vera's current status.
        self.status_label = tk.Label(root, text="Press the button to speak or type a message.", bg='#2c2f33', fg='#99aab5', font=("Helvetica Neue", 10))
        self.status_label.pack(pady=(0, 5))

        # Canvas for the speaking animation.
        self.canvas = tk.Canvas(root, width=300, height=100, bg='#2c2f33', highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Start the animation loop.
        self.start_animation()
        
        # Start the main logic thread after a delay.
        self.root.after(1000, self.start_listening_thread)

    def start_listening_thread(self):
        """Starts the background thread that listens for the 'Vera' hotword."""
        thread = threading.Thread(target=self.run_vera_logic)
        thread.daemon = True # Allows the main program to exit even if this thread is running.
        thread.start()

    def send_message(self, event=None):
        """Handles sending a typed message."""
        user_input = self.entry_box.get()
        if user_input:
            self.entry_box.delete(0, tk.END)
            # Process the user's input.
            self.process_input(user_input)
            
    def process_input(self, user_input):
        """Processes user input, whether from voice or text."""
        self.update_conversation("You", user_input)
        
        # Check for a special command to save the user's name.
        if "my name is" in user_input:
            name = user_input.split("is")[-1].strip()
            save_fact("name", name)
            # Speak a confirmation message in a separate thread.
            speak_thread = threading.Thread(target=speak, args=(f"Got it, I'll never forget that your name is {name}.",))
            speak_thread.start()
        else:
            # If it's not a special command, get a response from Vera.
            def respond():
                reply = get_vera_response(user_input)
                speak(reply)
            
            # Run the response generation and speaking in a separate thread.
            respond_thread = threading.Thread(target=respond)
            respond_thread.start()

    def update_conversation(self, sender, message):
        """Appends a message to the chat area."""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.config(state='disabled')
        # Automatically scroll to the bottom.
        self.chat_area.yview(tk.END)

    def update_status(self, text):
        """Updates the status label at the bottom of the GUI."""
        self.status_label.config(text=text)

    def start_animation(self):
        """Initializes the voice animation."""
        self.animating = True
        self.angle = 0
        self.animate()

    def animate(self):
        """The main animation loop. Redraws the canvas periodically."""
        if not self.animating:
            return
            
        self.canvas.delete("all")
        # If Vera is speaking, draw the dynamic wave animation.
        if is_speaking:
            num_bars = 10
            max_height = 50
            for i in range(num_bars):
                # Calculate the height of each bar using a sine wave for a smooth effect.
                angle_offset = self.angle + i * (360 / num_bars)
                height = max_height / 2 * (1 + math.sin(math.radians(angle_offset * 4 + self.angle * 2)))
                x0 = i * 30
                y0 = 50 - height / 2
                x1 = (i + 1) * 30 - 5
                y1 = 50 + height / 2
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='#7289da', outline="")
            self.angle += 5 # Increment the angle to make the wave move.
        else:
            # If Vera is not speaking, draw a simple flat line.
             self.canvas.create_line(10, 50, 290, 50, fill='#40444b', width=2)


        # Schedule the next frame of the animation.
        self.root.after(30, self.animate)

    def run_vera_logic(self):
        """The main loop that continuously listens for the hotword."""
        self.update_status("Vera is ready.")
        while True:
            # Listen for a command.
            command = listen()
            # If a command is heard and it contains the hotword "vera"...
            if command and "vera" in command:
                # ...process the command after removing the hotword.
                self.process_input(command.replace("vera", "").strip())
            time.sleep(1)


if __name__ == "__main__":
    # Create the main Tkinter window.
    root = tk.Tk()
    # Create an instance of the VeraApp.
    app = VeraApp(root)
    # Start the Tkinter event loop.
    root.mainloop()
