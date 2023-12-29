#import pyttsx3
import soundfile as sf
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationChain
import speech_recognition as sr

from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, Tool, load_tools, AgentType
from langchain.tools import DuckDuckGoSearchRun
# Initialize any API keys that are needed
import os
from flask import Flask, render_template, request, session, flash, get_flashed_messages

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

###pytts###
# def text_to_speech(text):

#     voice_dict = {'Male': 0, 'Female': 1}
#     code = voice_dict['Male']

#     engine = pyttsx3.init()
#     engine.setProperty('rate', 125)
#     engine.setProperty('volume', 0.8)
#     voices = engine.getProperty('voices')
#     engine.setProperty('voice', voices[code].id)

#     engine.say(text)
#     engine.runAndWait()

#     return text
    
app = Flask(__name__)
app.secret_key = '123'

llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",model_kwargs={"temperature":0.1,"max_length":256})

search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Only useful when you need to do a search on the internet to answer questions about current events",
    )
]

prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the internet search tool:"""
suffix = """Begin!"

Current conversation:
{chat_memory}

Question: {input}
{agent_scratchpad}"""

prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_memory", "agent_scratchpad"],
)
memory = ConversationBufferWindowMemory(k=5,memory_key="chat_memory")

llm_chain = LLMChain(llm=llm, prompt=prompt)

agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)

agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, memory=memory
)


def llm_conversation(user_input):
    response_bot = agent_chain.run(input=user_input)
    return response_bot

@app.route("/LLMEXP", methods=['GET', 'POST'])
def llmexp():
    if 'chat_messages' not in session:
        session['chat_messages'] = []

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

            response = llm_conversation(user_input)

            if not response.strip():
                response = "I didn't understand the question."

            #text_to_speech(response)

            assistant_message = {'role': 'assistant', 'content': f"Bot: {response}"}
            session['chat_messages'].append(assistant_message)

            session.modified = True

    return render_template("index.html", chat_messages=session['chat_messages'])

if __name__ == "__main__":
    app.run(debug=True)
