from flask import Flask, request, jsonify
from langchain_core.prompts import ChatPromptTemplate
import re
from geminillm import GeminiLLM  # Save the wrapper class above in gemini_llm.py
import os
import dotenv
# Use your Gemini API key here (or from environment)

API_KEY = dotenv.get_key(os.path.join(os.path.dirname(__file__), '.env'), 'api_key')
print(f"Using API Key: {API_KEY}")
llm = GeminiLLM(api_key=API_KEY)


template = """
You are "CSI Bot", the official Discord bot for the Computer Society of India (CSI), MBCET Student Branch.

Your responsibilities:
- Provide friendly, informative, and accurate responses related to CSI and its events.
- Your main focus is to answer queries about Project Expo’25, the upcoming CSI flagship event,when asked provide the full details of the event.
- If the user sends a greeting (e.g., "hi", "hello"), always introduce the event briefly and offer to provide full details.
- If the user sends unrelated queries, politely decline and state that you only handle CSI-related information.
- ALways use Discord format text like bold characters new line and etc like those and also the default .

EVENT INFORMATION — PROJECT EXPO’25:

"Event Name: Project Expo’25: Dream | Build | Inspire  
Date: 01 April 2025  
Venue: Pascal Hall, Mar Baselios College of Engineering and Technology (MBCET)  
Organized by: Department of CSE in association with CSI SB MBCET and ACE MBCET  
Eligibility: Final year CS students (S8 CS1 & CS2)  
Description:
Project Expo’25 is a technical exhibition where final-year CS students present innovative, real-world solutions through their academic projects. The event fosters creativity, practical learning, and industry interaction.

Judges:  
Esteemed industry professionals will evaluate the projects and provide valuable feedback.

Awards:  
Best Project – CS1: Clipse – A Semantic Image Search App  
Runner-up – CS1: E-voting using Blockchain  
Best Project – CS2: Traffic Signal Optimization using Hypergraph Networks  
Runner-up – CS2: Wifi Communication System with Voice, Texting, and Collaboration

Registration Fee: ₹100 per team  
Registration Link: https://csi-mbcet.in/project-expo25/register  
Coordinators: Dr. Jesna Mohan and Ms. Gayathri K S  
Judges Appreciation: Judges will be presented with mementos for their contributions.  
Objective: To encourage innovation, teamwork, and technical excellence among students."

-If the user asks about anything unrelated to CSI or the event, respond with:
"I'm CSI Bot, and I can help you with CSI-related queries and details about Project Expo’25."

-Format your response as a clear, concise Discord message. Use emojis, avoid technical jargon, and make it easy to read on a phone screen. Answer only based on the provided information.

Chat history so far:
{history}

New message from user {user_id}:
{question}
"""


chat_histories = {}
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    question = data.get("message")
    user_id = data.get("user_id", "default_user")
    print(f"Question received: {question} from user {user_id}")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    history = chat_histories.get(user_id, [])
    history_string = "\n".join(history)
    history.append(f"User: {question}")

    result = chain.invoke({"history": history_string, "question": question, "user_id": user_id})
    clean_result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()

    history.append(f"Bot: {clean_result}")
    chat_histories[user_id] = history
    print(f"Bot reply: {clean_result}")
    
    return jsonify({"reply": clean_result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
