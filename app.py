import streamlit as st
import os
import tempfile
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from dotenv import load_dotenv

# 1. Local .env file load karne ke liye
load_dotenv()

# Streamlit Page ki Setting - Yahan naam change kiya hai
st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

# 2. API Key setup
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API Key nahi mili! Kripya GitHub secrets ya .env file me add karein.")
    st.stop()

# Groq Client shuru karein
client = Groq(api_key=GROQ_API_KEY)

# --- HELPER FUNCTIONS ---

def get_free_search_results(query):
    """DuckDuckGo se free internet search karke data lata hai"""
    try:
        results = DDGS().text(query, max_results=3)
        snippets = [res['body'] for res in results]
        return "\n".join(snippets)
    except Exception as e:
        return ""

def text_to_audio(text):
    """Bot ke text jawab ko mp3 audio me badalta hai (gTTS)"""
    try:
        # lang='hi' Hindi tone ke liye hai
        tts = gTTS(text=text, lang='hi', slow=False) 
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio_file.name)
        return temp_audio_file.name
    except Exception as e:
        return None

# --- MAIN CHATBOT UI ---

# Yahan title change kiya hai
st.title("🤖 Jatin's Assistant")
st.caption("Main Jatin ka personal assistant hoon. Main internet par search kar sakta hoon aur aawaz mein jawab de sakta hoon!")

# Session state me messages history store karein
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages UI par dikhayein
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Naya user input
if prompt := st.chat_input("Mujhse kuch bhi puchiye..."):
    
    # User message UI pe dikhayein aur list me add karein
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Bot processing start
    with st.chat_message("assistant"):
        
        # Step 1: Web Search
        with st.spinner("Internet par search kar raha hoon... 🌐"):
            web_context = get_free_search_results(prompt)
            
        # Step 2: Groq se Jawab banana
        with st.spinner("Jawab soch raha hoon... 🤔"):
            # Yahan SYSTEM PROMPT mein bot ko uska naam bataya gaya hai
            system_prompt = f"""You are a helpful, smart, and friendly AI assistant named "Jatin's Assistant". 
            You were created by Jatin. Answer the user's question using the provided web search results. 
            If the answer is not in the results, use your own knowledge. Keep the answer clear and concise.
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
                )
                bot_response = completion.choices[0].message.content
                
                # Text answer dikhayein
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Step 3: Aawaz (Audio) generate karna
                with st.spinner("Aawaz generate kar raha hoon... 🔊"):
                    audio_file_path = text_to_audio(bot_response)
                    if audio_file_path:
                        st.audio(audio_file_path, format="audio/mp3", autoplay=True)
                        
            except Exception as e:
                st.error(f"Koi technical error aayi: {e}")
