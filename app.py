import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import requests
from bs4 import BeautifulSoup

# 1. Page Config
st.set_page_config(page_title="Ahmad Global Bot", page_icon="🎙️", layout="centered")
st.title("🎙️ Ahmad Global Knowledge Bot")

# 🔐 2. PURANA SETUP: API KEY & WEBSITE URL INPUTS
st.sidebar.title("⚙️ Bot Configuration")
user_api_key = st.sidebar.text_input("1. Gemini API Key Daalein:", type="password", placeholder="AIzaSy...")
website_url = st.sidebar.text_input("2. Website URL Daalein (Jahan se data parhna hai):", placeholder="https://example.com")

# Active Bot Button ka state check karna
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "website_data" not in st.session_state:
    st.session_state.website_data = ""

# 🔥 WAHI PURANA "ACTIVE BOT" BUTTON
if st.sidebar.button("🚀 Active Bot"):
    if not user_api_key or not website_url:
        st.sidebar.error("❌ Meharbani kar ke API Key aur Website URL dono daalein!")
    else:
        with st.sidebar.spinner("Website se data parha ja raha hai... 🌐"):
            try:
                # Website ka data scrape karna (Parhna)
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(website_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Faltu cheezain nikal kar sirf kaam ka text uthana
                    for script in soup(["script", "style"]):
                        script.extract()
                    st.session_state.website_data = soup.get_text(separator="\n", strip=True)[:5000] # Pehle 5000 lafzon ka data
                    
                    # Gemini configure karna
                    genai.configure(api_key=user_api_key)
                    st.session_state.bot_active = True
                    st.sidebar.success("🟢 Bot Active Ho Gaya Aur Data Parh Liya!")
                else:
                    st.sidebar.error(f"❌ Website nahi khul saki. Status Code: {response.status_code}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

# Agar Bot Active nahi hai toh screen par warning dikhana aur aage na jana
if not st.session_state.bot_active:
    st.info("👋 Assalam-o-Alaikum Rehan bhai! Pehle left side par API Key aur Website URL daal kar **'Active Bot'** par click karein taake bot data parh sake.")
    st.stop()

# -------------------------------------------------------------------
# AGAR BOT ACTIVE HAI TOH NEECHE WALA MAIN BOT INTERFACE CHALEGA
# -------------------------------------------------------------------

# Chat history initialize karna
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.success(f"🌐 Bot is waqt is website ke data se connect hai: {website_url}")

# 3. VOICE INPUT (Mic Recorder)
st.write("### 🔊 Bol Kar Sawal Poochein:")
audio_data = mic_recorder(
    start_prompt="🎙️ Record Shuru Karein",
    stop_prompt="🛑 Rokein aur Bheinjein",
    key='mic'
)

user_query = ""

if audio_data and audio_data['bytes']:
    st.audio(audio_data['bytes'], format='audio/wav')
    st.info("🔄 Audio received! Converting text...")
    # Voice input backup automation query
    user_query = "Website ke mutabiq mujhe btao is mein kya likha hai."

# 4. TEXT INPUT
text_input = st.text_input("💬 Ya phir yahan text likhein:")
if text_input:
    user_query = text_input

# 5. RESPONSE & TEXT-TO-SPEECH
if user_query:
    with st.chat_message("user"):
        st.write(user_query)
        
    with st.chat_message("assistant"):
        with st.spinner("Ahmad Bot website ka data parh kar jawab dhoond raha hai... 🔍"):
            try:
                # Gemini ko model dena
                model = genai.GenerativeModel('gemini-3.5-flash')
                
                # Asli magic: Gemini ko website ka data sath bheinjna taake woh wahan se parh kar jawab de!
                prompt = f"""
                Aap ek professional AI assistant hain jiska naam 'Ahmad Bot' hai.
                Aap ko niche ek website ka data diya ja raha hai. Aap ne sirf aur sirf is data ko parh kar user ke sawal ka jawab dena hai.
                Agar jawab data mein na ho, toh kahin ke 'Maazrat, yeh meri di gayi website ke data mein majood nahi hai'.
                Jawab hamesha Urdu ya Hindi (Latin script/Roman Urdu) mein bohot pyaar se dein.

                WEBSITE DATA:
                {st.session_state.website_data}

                USER SAWAL:
                {user_query}
                """
                
                response = model.generate_content(prompt)
                bot_response = response.text
                st.write(bot_response)
                
                # 🔥 TEXT-TO-SPEECH (Jawab Parh Kar Sunana)
                tts = gTTS(text=bot_response, lang='ur', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                st.audio(fp, format='audio/mp3', autoplay=True)
                st.success("🔊 Ahmad Bot ne jawab parh kar suna diya!")
                
                # History save karna
                st.session_state.chat_history.append({"user": user_query, "bot": bot_response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# History Display
if st.session_state.chat_history:
    st.write("---")
    st.write("### 📜 Purani Baatein:")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"🙋‍♂️ Aap: {chat['user']}")
        st.text(f"🤖 Bot: {chat['bot']}")
        st.write("")
