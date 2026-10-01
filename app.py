import streamlit as st
import requests
import os
import io
import base64
from dotenv import load_dotenv
from gtts import gTTS

# .env file load karein
load_dotenv()

# Page ka title aur icon set karein
st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

st.title("🤖 Jatin's Assistant")
st.caption("Aapka personal AI Assistant. Type karein aur jawab sunein!")

# -----------------------------
# Ask AI Function (Same API logic)
# -----------------------------
def ask_ai(question):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: API key nahi mili. Please .env file check karein."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": (
                        "You are Jatin's Assistant, a helpful voice assistant. "
                        "Give short and clear answers (1-3 sentences maximum).\n\n"
                        f"User: {question}"
                    )}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if "error" in result:
            # Ye line aapko screen par exact error bata degi
            return f"API Error: {result['error']['message']}"
            
        answer_text = result["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = answer_text.replace("*", "").replace("#", "").strip()
        return clean_text

    except Exception as e:
        return "Sorry, connection error."

# -----------------------------
# Autoplay Audio Function
# -----------------------------
def autoplay_audio(text):
    try:
        # Text ko audio mein convert karein
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Audio ko base64 mein convert karke HTML tag ke through auto-play karein
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        pass

# -----------------------------
# Chat UI (ChatGPT jaisa Interface)
# -----------------------------
# Chat history save karne ke liye session state ka use
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am Jatin's Assistant. How can I help you?"})
    autoplay_audio("Hello! I am Jatin's Assistant. How can I help you?")

# Purani chat history dikhayein
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input lein
if prompt := st.chat_input("Ask me anything..."):
    # User ka message screen par dikhayein
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # User message ko history mein save karein
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI se jawab mangein
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_ai(prompt)
            st.markdown(response)
            
            # AI ke jawab ko history mein save karein
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # AI ka jawab bol kar sunayein
            autoplay_audio(response)