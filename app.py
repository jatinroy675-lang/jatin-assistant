import streamlit as st
import os
import tempfile
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from dotenv import load_dotenv

# Local .env file load karne ke liye
load_dotenv()

st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

# API Key setup
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API Key nahi mili! Kripya GitHub secrets ya .env file me add karein.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- HELPER FUNCTIONS ---

def get_free_search_results(query):
    try:
        results = DDGS().text(query, max_results=3)
        snippets = [res['body'] for res in results]
        return "\n".join(snippets)
    except Exception as e:
        return ""

def text_to_audio(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False) 
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio_file.name)
        return temp_audio_file.name
    except Exception as e:
        return None

# --- MAIN CHATBOT UI ---

st.title("🤖 Jatin's Assistant")
st.caption("Main Jatin ka personal assistant hoon. Main internet par search kar sakta hoon aur aawaz mein jawab de sakta hoon!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mujhse kuch bhi puchiye..."):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        
        with st.spinner("Internet par search kar raha hoon... 🌐"):
            web_context = get_free_search_results(prompt)
            
            # Background data dekhne ke liye (debugging)
            with st.expander("🔍 Background Search Data Dekhein"):
                st.write(web_context if web_context else "Kuch nahi mila.")
            
        with st.spinner("Jawab soch raha hoon... 🤔"):
            
            # YAHAN SYSTEM PROMPT UPDATE KIYA HAI - AB YE APNA DIMAG BHI LAGAYEGA
            system_prompt = f"""You are Jatin's Assistant, a smart AI created by Jatin. 
            First, try to answer the user's question using the Web Search Results provided below. 
            If the Web Search Results are empty or do not contain the answer, you MUST use your own general knowledge to give the correct answer.
            Keep the answer very short, clear, and direct (maximum 1-2 sentences). Reply in the language the user used (Hindi/Hinglish/English).
            
            Web Search Results:
            {web_context}"""
            
            try:
                completion = client.chat.completions.create(
                    model="qwen/qwen3.8-27b", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=250
                )
                bot_response = completion.choices[0].message.content
                
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                with st.spinner("Aawaz generate kar raha hoon... 🔊"):
                    audio_file_path = text_to_audio(bot_response)
                    if audio_file_path:
                        st.audio(audio_file_path, format="audio/mp3", autoplay=True)
                        
            except Exception as e:
                st.error(f"Koi technical error aayi: {e}")
