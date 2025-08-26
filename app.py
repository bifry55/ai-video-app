import streamlit as st
from gtts import gTTS
from moviepy.editor import *
import os
import uuid

st.set_page_config(page_title="AI Video Ad Generator", layout="wide")

st.title("🎬 AI Video Ad Generator")
st.write("Masukkan deskripsi produk/layanan, lalu generate video iklan otomatis.")

# --- Input deskripsi
deskripsi = st.text_area("📝 Masukkan Deskripsi (copy-paste dari LP)")

# --- Pilihan user
voice_gender = st.selectbox("Pilih Suara Narasi", ["Wanita", "Pria"])
video_ratio = st.selectbox("Pilih Rasio Video", ["16:9", "9:16", "1:1"])
style = st.selectbox("Pilih Gaya Video", ["Cinematic", "Casual", "Slideshow"])

if st.button("🚀 Generate Video"):
    if deskripsi.strip() == "":
        st.warning("Harap masukkan deskripsi terlebih dahulu.")
    else:
        with st.spinner("🎥 Sedang membuat video..."):
            # --- Generate TTS
            tts = gTTS(deskripsi, lang='id')
            audio_file = f"{uuid.uuid4()}.mp3"
            tts.save(audio_file)

            # --- Dummy image (1 background saja biar cepat)
            img_file = "https://picsum.photos/1280/720"

            # --- Buat video clip
            clip = ImageClip(img_file).set_duration(10)
            audio = AudioFileClip(audio_file)
            final = clip.set_audio(audio)

            # --- Export video
            output_file = f"{uuid.uuid4()}.mp4"
            final.write_videofile(output_file, fps=24)

            st.success("✅ Video berhasil dibuat!")
            st.video(output_file)
            with open(output_file, "rb") as file:
                st.download_button("⬇️ Download Video", file, file_name="video_iklan.mp4")
