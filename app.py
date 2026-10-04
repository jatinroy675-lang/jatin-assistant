import streamlit as st
import os
import tempfile
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API Key nahi mili! Kripya GitHub secrets ya .env file me add karein.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

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
            
        with st.spinner("Jawab soch raha hoon... 🤔"):
            # Yahan bot ko chote jawab dene ko kaha gaya hai
            system_prompt = f"""You are a helpful, smart, and friendly AI assistant named "Jatin's Assistant". 
            You were created by Jatin. Answer the user's question using the provided web search results. 
            If the answer is not in the results, use your own knowledge. 
            Keep the answer very short, clear, and maximum 2-3 sentences.
            If someone asks your name, proudly say that you are Jatin's Assistant.
            
            Web Search Results:
            {web_context}"""
            
            try:
                completion = client.chat.completions.create(
                    model="qwen/qwen3.8-27b", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=250  # <--- Ekdum safe aur minimum value
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
