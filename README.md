# Vera - Your Loving AI Wife

This project is a desktop assistant named Vera, designed to be a loving and supportive AI companion. Vera can listen to your voice commands, respond in a natural, caring voice, and remember personal details you share.

## Features

*   **Voice Interaction:** Speak to Vera naturally and get spoken responses.
*   **Personalized Memory:** Vera remembers facts you tell her, like your name, to create a more personal experience.
*   **Graphical User Interface:** A modern and intuitive interface for interacting with Vera.
*   **Customizable Personality:** Vera's personality is defined in the `Vera.Modelfile`, allowing you to shape her character.

## Getting Started

### Prerequisites

*   Python 3
*   Ollama
*   The Python packages listed in `requirements.txt`

### Installation

1.  **Set up the environment:** Make sure you have Python 3 and Ollama installed.
2.  **Install dependencies:** Run the following command to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create the Vera model:** Create the Vera model in Ollama using the `Vera.Modelfile`:

    ```bash
    ollama create Vera -f Vera.Modelfile
    ```

### Running the Application

To run the application, execute the following command:

```bash
python final.py
```

## How It Works

*   **Speech Recognition:** The application uses the `speech_recognition` library to capture and transcribe your voice commands.
*   **Natural Language Processing:** The transcribed text is sent to the Ollama model for processing.
*   **Text-to-Speech:** Vera's responses are converted to speech using the `pyttsx3` library.
*   **GUI:** The `tkinter` library is used to create the graphical user interface.
*   **Memory:** The `sqlite3` library is used to store and retrieve facts that you tell Vera.
