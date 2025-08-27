import streamlit as st
import tempfile, os
from google.cloud import texttospeech
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="AI Video Maker", layout="wide")
st.title("🎬 AI Video Maker - 4 Angle Generator")

# ===== Google TTS Setup =====
json_str = st.secrets["general"]["GOOGLE_TTS_JSON"]

with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
    f.write(json_str.encode())
    creds_path = f.name

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
tts_client = texttospeech.TextToSpeechClient()

# ===== User Input =====
desc = st.text_area("📋 Masukkan Deskripsi LP", height=200)
resolution = st.selectbox("📐 Pilih Resolusi Video", ["720p", "1080p"])
generate_btn = st.button("Generate 4 Angle Scripts & Preview")

# ===== Dummy AI Script Generator =====
def generate_scripts(description):
    angles = ["FOMO", "Edukasi", "Testimonial", "Direct Offer"]
    return [f"{angle} Angle Script: {description}" for angle in angles]

# ===== Google TTS Function =====
def generate_tts_google(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code='id-ID', ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_audio.write(response.audio_content)
    tmp_audio.close()
    return tmp_audio.name

# ===== Preview Video Function =====
def generate_preview_video(script_text):
    img_url = "https://via.placeholder.com/720x480.png?text=Video+Preview"
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp_img.name)

    audio_file = generate_tts_google(script_text)
    clip = ImageClip(tmp_img.name).set_duration(5)
    audio_clip = AudioFileClip(audio_file)
    clip = clip.set_audio(audio_clip)
    return clip

# ===== Main =====
if generate_btn and desc.strip() != "":
    scripts = generate_scripts(desc)
    st.subheader("🎞 4 Angle Scripts Generated:")

    previews = []
    for i, script in enumerate(scripts):
        st.markdown(f"**Angle {i+1}:** {script}")
        preview_clip = generate_preview_video(script)
        previews.append(preview_clip)
        st.video(preview_clip.preview(fps=24, audio=True))

    if st.button("Generate Final 4 Videos"):
        st.success("✅ Generating final videos...")
        for i, clip in enumerate(previews):
            final_path = f"final_video_angle_{i+1}.mp4"
            clip.write_videofile(final_path, fps=24)
            st.video(final_path)
        st.success("🎉 4 Final Videos Generated!")
