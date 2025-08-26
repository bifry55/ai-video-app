import streamlit as st
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import tempfile

st.set_page_config(page_title="AI Video Generator", layout="centered")
st.title("🎬 AI Video Generator - Stable Version")

# Input teks deskripsi
narasi = st.text_area("Masukkan deskripsi / LP", height=150)

# Pilihan suara
voice = st.radio("Pilihan Suara", ["Wanita", "Pria"])

# Durasi video
durasi = st.slider("Durasi Video (detik)", 5, 60, 15)

# Upload background image
bg_image_file = st.file_uploader("Upload background image (opsional)", type=["jpg","png"])

if st.button("Generate Video"):
    if not narasi.strip():
        st.warning("Harap masukkan deskripsi dulu!")
    else:
        with st.spinner("Sedang membuat video... ⏳"):
            # ---- 1. Generate Audio ----
            tts = gTTS(narasi, lang='id', tld='com')  # bisa ganti tld=co.id/ com.au kalau mau variasi suara
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(audio_temp.name)

            # ---- 2. Generate Video ----
            if bg_image_file:
                # Pakai image upload
                img = Image.open(bg_image_file)
                img_clip = ImageClip(img).set_duration(durasi).resize(height=480)
                video_clip = img_clip.set_position("center")
            else:
                # Background hitam polos
                video_clip = ColorClip(size=(720,480), color=(0,0,0), duration=durasi)

            # Tambah teks overlay
            txt_clip = TextClip(narasi, fontsize=30, color='white', size=(700, None), method='caption')
            txt_clip = txt_clip.set_duration(durasi).set_position('center')

            # Load audio
            audio_clip = AudioFileClip(audio_temp.name).set_duration(durasi)

            # Merge video + teks + audio
            final_clip = CompositeVideoClip([video_clip, txt_clip])
            final_clip = final_clip.set_audio(audio_clip)

            # Simpan hasil video sementara
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            final_clip.write_videofile(output_file.name, fps=24, codec="libx264", audio_codec="aac")

            st.success("✅ Video berhasil dibuat!")
            st.video(output_file.name)
            with open(output_file.name, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="tvc_output.mp4", mime="video/mp4")
