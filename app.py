import streamlit as st
import io
import base64
from gtts import gTTS
from groq import Groq

# Page ka title aur icon set karein
st.set_page_config(page_title="Jatin's Assistant", page_icon="🤖")

st.title("🤖 Jatin's Assistant")
st.caption("Aapka personal AI Assistant. Type karein aur jawab sunein!")

# -----------------------------
# Ask AI Function (Optimized Tokens)
# -----------------------------
def ask_ai(question):
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return "Error: API key nahi mili. Please Streamlit secrets check karein."
    
    try:
        client = Groq(api_key=api_key)
        
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You are Jatin's Assistant, a helpful voice assistant. Give short and clear answers (1-3 sentences maximum)."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.6,
            # Yahan tokens ko 2048 se ghatakar 200 kar diya gaya hai taki error na aaye
            max_completion_tokens=200, 
            top_p=0.95,
            stream=False 
        )
        
        answer_text = completion.choices[0].message.content
        return answer_text.strip()

    except Exception as e:
        return f"API Error: {str(e)}"

# -----------------------------
# Autoplay Audio Function
# -----------------------------
def autoplay_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
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
# Chat UI 
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am Jatin's Assistant. How can I help you?"})
    autoplay_audio("Hello! I am Jatin's Assistant. How can I help you?")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_ai(prompt)
            st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            autoplay_audio(response)
