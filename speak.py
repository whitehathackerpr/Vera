import pyttsx3

def speak_as_vera(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # voices[1] is usually the female voice on Windows/Linux
    engine.setProperty('voice', voices[1].id) 
    engine.setProperty('rate', 170) # Natural speed
    engine.say(text)
    engine.runAndWait()