import streamlit as st
from gtts import gTTS
import ffmpeg
import os

st.set_page_config(page_title="AI Video App", layout="centered")

st.title("🎬 AI Video App - Dengan Background Gambar")

# Input teks
text_input = st.text_area("Masukkan teks narasi", "Halo, ini contoh narasi AI video.")

# Upload gambar background
bg_image = st.file_uploader("Upload gambar background (jpg/png)", type=["jpg", "jpeg", "png"])

if st.button("Generate Video"):
    # 1. Generate audio dari teks
    tts = gTTS(text_input, lang="id")
    audio_file = "output.mp3"
    tts.save(audio_file)

    # 2. Cek durasi audio dengan ffmpeg
    probe = ffmpeg.probe(audio_file)
    duration = float(probe['format']['duration'])

    # 3. Tentukan background
    if bg_image:
        bg_file = "background.png"
        with open(bg_file, "wb") as f:
            f.write(bg_image.read())
    else:
        bg_file = None

    video_file = "output.mp4"

    if bg_file:
        # Video dengan gambar background
        (
            ffmpeg
            .input(bg_file, loop=1, framerate=30)
            .filter('scale', 1280, 720)
            .output(audio_file, video_file, vcodec='libx264', acodec='aac', shortest=None, pix_fmt='yuv420p', t=duration)
            .run(overwrite_output=True)
        )
    else:
        # Video hitam polos
        (
            ffmpeg
            .input(f'color=c=black:s=1280x720:d={duration}', f='lavfi')
            .output(audio_file, video_file, vcodec='libx264', acodec='aac', pix_fmt='yuv420p')
            .run(overwrite_output=True)
        )

    st.success("✅ Video berhasil dibuat!")
    st.video(video_file)
    st.audio(audio_file)
