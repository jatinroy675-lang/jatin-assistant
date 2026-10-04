import streamlit as st
import os
import tempfile
import base64
from groq import Groq
from tavily import TavilyClient
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.error("API Keys missing hain! Kripya secrets ya .env file check karein.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def get_tavily_search_results(query):
    try:
        response = tavily_client.search(query=query, search_depth="basic", max_results=3)
        snippets = [result['content'] for result in response.get('results', [])]
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
        
        with st.spinner("Search kar raha hoon... 🌐"):
            web_context = get_tavily_search_results(prompt)
            
        with st.spinner("Jawab soch raha hoon... 🤔"):
            
            system_prompt = f"""You are Jatin's Assistant, a smart AI created by Jatin. 
            First, try to answer the user's question using the Search Results provided below. 
            If the Search Results are empty or do not contain the answer, you MUST use your own general knowledge to give the correct answer.
            Keep the answer very short, clear, and direct (maximum 1-2 sentences). Reply in the language the user used (Hindi/Hinglish/English).
            
            Search Results:
            {web_context}"""
            
            try:
                completion = groq_client.chat.completions.create(
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
                        with open(audio_file_path, "rb") as f:
                            audio_bytes = f.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                        audio_html = f"""
                            <audio autoplay hidden>
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Koi technical error aayi: {e}")
