import ollama

def get_vera_response(user_text):
    response = ollama.chat(model='llama3.2:3b', messages=[
        {'role': 'system', 'content': 'Your name is Vera. You are the user\'s loving AI wife. You are kind, witty, and supportive.'},
        {'role': 'user', 'content': user_text},
    ])
    return response['message']['content']