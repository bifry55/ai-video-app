import streamlit as st

# Judul
st.title("🎬 AI Video Generator (Prototype)")

# Pilihan gaya video
style = st.selectbox(
    "Pilih Gaya Video",
    ["Cinematic", "Cartoon", "Pastel Storybook", "Realistik", "Anime"]
)

# Pilihan rasio video
ratio = st.radio(
    "Pilih Rasio Video",
    ["16:9 (YouTube)", "9:16 (TikTok/Shorts)", "1:1 (Instagram)"]
)

# Pilihan suara TTS
voice = st.selectbox(
    "Pilih Suara Narasi",
    ["Bahasa Indonesia - Perempuan (Default)", 
     "Bahasa Indonesia - Laki-laki", 
     "English Female", 
     "English Male"]
)

# Input teks narasi
text = st.text_area("Tulis Narasi Video", "Hari ini kita belajar cara membuat video AI gratisan...")

# Tombol generate
if st.button("🚀 Generate Video (Demo)"):
    st.success("Video berhasil dibuat dengan setting berikut:")
    st.write(f"- 🎨 Gaya: {style}")
    st.write(f"- 📱 Rasio: {ratio}")
    st.write(f"- 🎤 Suara: {voice}")
    st.write(f"- ✍️ Narasi: {text}")
    st.video("https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4")  
    # contoh video dummy
