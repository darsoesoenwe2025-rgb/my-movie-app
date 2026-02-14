import streamlit as st
import google.generativeai as genai
import yt_dlp
import os
import asyncio
import edge_tts

# --- UI Setup ---
st.set_page_config(page_title="AI Movie Recap", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: white; }
    .setup-box { border: 1px solid #2d3139; padding: 20px; border-radius: 15px; background-color: #161b22; margin-bottom: 20px; }
    .stTextInput>div>div>input { background-color: #0b0e14; color: white; border: 1px solid #2d3139; border-radius: 10px; height: 45px; }
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #7d32e6, #a371f7); color: white; height: 3.5em; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 AI Movie Recap")

# 1. API SETUP
api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste Gemini API Key...")
if api_key:
    genai.configure(api_key=api_key)

# 2. VIDEO SOURCE
video_url = st.text_input("VIDEO SOURCE", placeholder="Paste TikTok Link here...")
uploaded_file = st.file_uploader("OR UPLOAD CLIP", type=["mp3", "mp4", "wav", "m4a"])

# 3. AI PERSONA
voice_map = {"Bright & Clear (Female)": "my-MM-NilarNeural", "Thiha (Male)": "my-MM-ThihaNeural"}
selected_voice = st.selectbox("Voice Character", list(voice_map.keys()))

# Functions
def download_audio(url):
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'temp_audio.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "temp_audio.mp3"

# Start Button
if st.button("▶️ START LIVE AI SESSION"):
    if not api_key: st.error("Please enter Gemini API Key.")
    elif not video_url and not uploaded_file: st.error("Please provide a Link or File.")
    else:
        with st.spinner("Processing..."):
            try:
                audio_path = download_audio(video_url) if video_url else "temp.mp3"
                if not video_url:
                    with open(audio_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([genai.upload_file(path=audio_path), "Create a viral Myanmar movie recap script. Output ONLY Myanmar text."])
                myanmar_text = response.text
                st.text_area("Script:", myanmar_text, height=150)
                
                asyncio.run(edge_tts.Communicate(myanmar_text, voice_map[selected_voice]).save("final.mp3"))
                st.audio("final.mp3")
                os.remove(audio_path)
            except Exception as e: st.error(f"Error: {str(e)}")
