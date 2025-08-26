import streamlit as st
from gtts import gTTS
from moviepy.editor import *
import tempfile
import os

st.set_page_config(page_title="AI TVC Generator", page_icon="🎬", layout="centered")

st.title("🎬 AI TVC Generator")
st.write("Masukkan deskripsi iklanmu, pilih suara narasi, dan hasilkan video singkat otomatis!")

# Input user
deskripsi = st.text_area("📝 Masukkan deskripsi iklan (copy dari LP)", height=200)

# Pilihan suara
gender = st.selectbox("🗣️ Pilih suara narator", ["Pria 1", "Pria 2", "Wanita 1", "Wanita 2"])

if st.button("🚀 Generate Video"):
    if deskripsi.strip() == "":
        st.warning("Harap masukkan deskripsi dulu.")
    else:
        with st.spinner("Sedang membuat video... tunggu sebentar ⏳"):
            # ---- 1. Generate Audio ----
            # Mapping sederhana: semua suara pakai gTTS (beda aksen aja)
            lang = "id"
            tts = gTTS(deskripsi, lang=lang)
            
            # Simpan audio sementara
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_audio.name)

            # ---- 2. Generate Video ----
            # Background sederhana: layar putih
            clip = ColorClip(size=(720, 480), color=(255, 255, 255), duration=10)

            # Tambah teks
            txt_clip = TextClip(deskripsi, fontsize=32, color='black', size=(700, 400), method="caption")
            txt_clip = txt_clip.set_duration(10).set_position("center")

            # Audio
            audio_bg = AudioFileClip(temp_audio.name)

            # Merge video + audio
            final = CompositeVideoClip([clip, txt_clip])
            final = final.set_audio(audio_bg)

            # Simpan ke file sementara
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            final.write_videofile(temp_video.name, codec="libx264", audio_codec="aac")

            # ---- 3. Tampilkan Hasil ----
            st.success("✅ Video berhasil dibuat!")
            st.video(temp_video.name)
            with open(temp_video.name, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="tvc_output.mp4", mime="video/mp4")

            # Cleanup
            os.remove(temp_audio.name)
