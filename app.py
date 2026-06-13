import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import requests
from bs4 import BeautifulSoup

# 1. Page Config & Top Banner
st.set_page_config(page_title="Ahmad Global Bot", page_icon="🤖", layout="centered")

# 🔥 HIDE GITHUB & STREAMLIT OPTIONS (Fuzool options khatam karne ka jadoo)
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}       /* Streamlit main menu chupanay k liye */
        header {visibility: hidden;}          /* Top GitHub icon aur decoration chupanay k liye */
        footer {visibility: hidden;}          /* Footer text chupanay k liye */
        div.stDeployButton {display: none;}   /* Deploy button hatane k liye */
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("🤖 Ahmad Global Intelligent Bot")
st.write("---")

# Session States initialize karna
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "website_data" not in st.session_state:
    st.session_state.website_data = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🔑 2. MAIN SCREEN CONFIGURATION (Activation & Knowledge Base)
st.subheader("⚙️ Bot Activation & Knowledge Base")

user_api_key = st.text_input("1. Enter Gemini API Key:", type="password", placeholder="AIzaSy...")
website_url = st.text_input("2. Enter Website URL (Jahan se bot data parhay ga):", placeholder="https://example.com")

# "ACTIVE BOT" BUTTON
if st.button("🚀 Active Bot"):
    if not user_api_key or not website_url:
        st.error("❌ Meharbani kar ke API Key aur Website URL dono laazmi daalein!")
    else:
        with st.spinner("Website ka data khoncha ja raha hai... 🌐"):
            try:
                # Web Scraping to read data
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(website_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Faltu tags nikalna
                    for script in soup(["script", "style"]):
                        script.extract()
                    st.session_state.website_data = soup.get_text(separator="\n", strip=True)[:5000]
                    
                    # Gemini setup
                    genai.configure(api_key=user_api_key)
                    st.session_state.bot_active = True
                    st.success("🟢 Ahmad Bot Active Ho Gaya Hai! Ab Aap Sawal Pooch Sakte Hain.")
                else:
                    st.error(f"❌ Website data nahi parha ja saka. Status Code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.write("---")

# -------------------------------------------------------------------
# CHAT INTERFACE (Active hone k baad)
# -------------------------------------------------------------------
if st.session_state.bot_active:
    st.subheader("💬 Chat with Ahmad Bot")
    st.info(f"Connected Website: {website_url}")

    # VOICE INPUT (Mic Recorder)
    st.write("🎤 **Bol Kar Sawal Poochein:**")
    audio_data = mic_recorder(
        start_prompt="🎙️ Record Shuru",
        stop_prompt="🛑 Rokein aur Bheinjein",
        key='mic'
    )

    user_query = ""

    if audio_data and audio_data['bytes']:
        st.audio(audio_data['bytes'], format='audio/wav')
        st.info("🔄 Awaaz processing mein hai...")
        user_query = "Website ke data ke mutabiq mujhe detail batao."

    # TEXT INPUT
    text_input = st.text_input("✍️ Ya phir yahan text likhein:")
    if text_input:
        user_query = text_input

    # RESPONSE GENERATION & VOICE OUTPUT
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Ahmad Bot website par research kar raha hai... 🔍"):
                try:
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    
                    prompt = f"""
                    Aap ek professional AI assistant hain jiska naam 'Ahmad Bot' hai.
                    Aap ko niche ek website ka data diya ja raha hai. Aap ne sirf aur sirf is data ko parh kar user ke sawal ka jawab dena hai.
                    Agar jawab data mein na ho, toh saaf kahin ke 'Maazrat, yeh meri di gayi website ke data mein majood nahi hai'.
                    Jawab hamesha Roman Urdu (Latin script) mein bohot tameez aur pyaar se dein.

                    WEBSITE DATA:
                    {st.session_state.website_data}

                    USER SAWAL:
                    {user_query}
                    """
                    
                    response = model.generate_content(prompt)
                    bot_response = response.text
                    st.write(bot_response)
                    
                    # TEXT-TO-SPEECH (Voice Output)
                    tts = gTTS(text=bot_response, lang='ur', slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    
                    st.audio(fp, format='audio/mp3', autoplay=True)
                    st.success("🔊 Ahmad Bot ne jawab parh kar suna diya!")
                    
                    st.session_state.chat_history.append({"user": user_query, "bot": bot_response})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Chat History
    if st.session_state.chat_history:
        st.write("---")
        st.write("### 📜 Purani Guftagu:")
        for chat in reversed(st.session_state.chat_history):
            st.text(f"🙋‍♂️ Aap: {chat['user']}")
            st.text(f"🤖 Bot: {chat['bot']}")
            st.write("")
