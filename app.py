import pyttsx3
import soundfile as sf
from langchain.llms import HuggingFaceHub
import speech_recognition as sr
# Initialize any API keys that are needed
import os
from flask import Flask, render_template, request, session, flash, get_flashed_messages

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

###pytts###
def text_to_speech(text):

    voice_dict = {'Male': 0, 'Female': 1}
    code = voice_dict['Male']

    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    engine.setProperty('volume', 0.8)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[code].id)

    engine.say(text)
    engine.runAndWait()

    return text
    
app = Flask(__name__)
app.secret_key = '123'
@app.route("/LLMEXP", methods=['GET', 'POST'])
def llmexp():
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    conversation = HuggingFaceHub(repo_id="google/flan-t5-base", model_kwargs={"temperature": 0.1, "max_length": 256})

    if request.method == 'POST':
        if 'record_audio' in request.form:
            # Record audio and convert to text
            user_input = request.form['user_input']
        else:
            # User input from textarea
            user_input = request.form['user_input']

        if not user_input or user_input.isspace():
            flash("Please provide a valid input.")
            
        else:
            user_message = {'role': 'user', 'content': f"User: {user_input}"}
            session['chat_messages'].append(user_message)

            response = conversation(user_input)

            if not response.strip():
                response = "I didn't understand the question."

            text_to_speech(response)
            
            assistant_message = {'role': 'assistant', 'content': f"Bot: {response}"}
            session['chat_messages'].append(assistant_message)

            session.modified = True

    return render_template("index.html", chat_messages=session['chat_messages'])


    
