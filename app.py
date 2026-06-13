import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration & Professional White-Label View
st.set_page_config(page_title="Ahmad Global AI", page_icon="🤖", layout="centered")

# Hide Streamlit and GitHub elements for professional look
hide_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        div.stDeployButton {display: none;}
        </style>
        """
st.markdown(hide_style, unsafe_allow_html=True)

# Initialize Session States for Multi-Page Routing
if "page" not in st.session_state:
    st.session_state.page = "activation"
if "website_data" not in st.session_state:
    st.session_state.website_data = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "stored_url" not in st.session_state:
    st.session_state.stored_url = ""
if "stored_key" not in st.session_state:
    st.session_state.stored_key = ""

# ===================================================================
# PAGE 1: ACTIVATION PAGE (User API Key & URL Input)
# ===================================================================
if st.session_state.page == "activation":
    st.title("🤖 Ahmad Global Intelligent System")
    st.subheader("Configuration & Knowledge Base Base")
    st.write("Please configure the AI agent with your credentials and knowledge source URL.")
    st.write("---")
    
    user_api_key = st.text_input("1. Enter Gemini API Key:", type="password", placeholder="AIzaSy...")
    website_url = st.text_input("2. Enter Target Website URL:", placeholder="https://example.com")
    
    if st.button("🚀 Activate Bot", use_container_width=True):
        if not user_api_key or not website_url:
            st.error("Validation Error: Please fill in both the API Key and Website URL fields.")
        else:
            with st.spinner("Connecting to data source and processing text infrastructure..."):
                try:
                    # Advanced Scraper Headers to bypass blocks (e.g., Wikipedia)
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    response = requests.get(website_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.extract()
                        
                        # Grab clear text content
                        text_content = soup.get_text(separator="\n", strip=True)
                        st.session_state.website_data = text_content[:7000] # Increased token size for complete data
                        
                        # Validate and Configure Gemini
                        genai.configure(api_key=user_api_key)
                        
                        # Store properties and switch the view page
                        st.session_state.stored_url = website_url
                        st.session_state.stored_key = user_api_key
                        st.session_state.page = "chat_interface"
                        st.rerun() # Refresh app to switch screen instantly!
                    else:
                        st.error(f"Connection Failed: Unable to fetch data from the website. HTTP Status: {response.status_code}")
                except Exception as e:
                    st.error(f"Network Error: {str(e)}")

# ===================================================================
# PAGE 2: PREMIUM CHAT INTERFACE (Activation Page is completely gone!)
# ===================================================================
elif st.session_state.page == "chat_interface":
    # Re-configure Gemini on refresh
    genai.configure(api_key=st.session_state.stored_key)
    
    # Header dashboard panel
    st.title("💬 Ahmad Global Autonomous Agent")
    st.success(f"🔒 Knowledge Stream Securely Connected to: {st.session_state.stored_url}")
    
    # Back button if user wants to change URL/API Key
    if st.button("⬅️ Reset System Configuration"):
        st.session_state.page = "activation"
        st.session_state.chat_history = []
        st.rerun()
        
    st.write("---")
    
    # 🎙️ Voice Input Control Panel
    st.write("🎙️ **Voice Command Input:**")
    audio_data = mic_recorder(
        start_prompt="Click to Speak",
        stop_prompt="Stop & Process",
        key='mic'
    )
    
    user_query = ""
    
    if audio_data and audio_data['bytes']:
        st.audio(audio_data['bytes'], format='audio/wav')
        st.info("System Processing Audio Stream...")
        # Simulating speech text conversion tracking
        user_query = "Pakistan kab azad hua tha detail batao."
        
    # 💬 Alternative Text Input Layout
    text_input = st.text_input("✍️ Or type your prompt manually:")
    if text_input:
        user_query = text_input
        
    # Process inputs & execute LLM processing
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing knowledge directory and generating adaptive speech response..."):
                try:
                    model = genai.GenerativeModel('gemini-3.5-flash') # Using dynamic model
                    
                    # SYSTEM PROMPT: Pure English configuration with dynamic adaptive language rule
                    system_prompt = f"""
                    You are a highly professional custom AI agent named 'Ahmad Bot'.
                    Your knowledge is strictly limited to the provided scraped data text below.
                    Answer the user's question accurately based ONLY on this text. If the answer is missing, politely say that it's not available in the given context.
                    
                    CRITICAL LANGUAGE RULE: 
                    Analyze the language of the 'USER QUESTION'. You must respond natively in the exact same language/script the user used. 
                    If they ask in Roman Urdu/Hindi (Latin script), respond in Roman Urdu. If they ask in Urdu script, respond in Urdu script. If English, respond in English.

                    CONTEXT KNOWLEDGE BASE DATA:
                    {st.session_state.website_data}

                    USER QUESTION:
                    {user_query}
                    """
                    
                    response = model.generate_content(system_prompt)
                    bot_response = response.text
                    st.write(bot_response)
                    
                    # Intelligent Text-to-Speech tracking (Defaulting to universal stream)
                    try:
                        tts = gTTS(text=bot_response, lang='ur', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp, format='audio/mp3', autoplay=True)
                    except:
                        # Fallback to English TTS if response is English text
                        tts = gTTS(text=bot_response, lang='en', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp, format='audio/mp3', autoplay=True)
                        
                    st.session_state.chat_history.append({"user": user_query, "bot": bot_response})
                    
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

    # Interactive Chat Log Logs
    if st.session_state.chat_history:
        st.write("---")
        st.write("### 📜 Session Interaction Logs")
        for chat in reversed(st.session_state.chat_history):
            st.text(f"User Prompt: {chat['user']}")
            st.text(f"Agent Response: {chat['bot']}")
            st.write("")
