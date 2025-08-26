import streamlit as st
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import textwrap, tempfile, os, numpy as np

st.set_page_config(page_title="AI Video Ultimate Cinematic Editor", layout="centered")
st.title("🎬 AI Video Ultimate Cinematic Editor + Preview Mode")

# --- User Inputs ---
narasi = st.text_area("Masukkan Deskripsi / LP", height=150)
voice = st.radio("Pilihan Suara Narasi", ["Wanita", "Pria"])
highlight_words = st.text_input("Highlight kata kunci (pisahkan koma)", "")
durasi_total = st.slider("Durasi Video Total (detik)", 5, 120, 20)
resolusi = st.selectbox("Resolusi Video", ["480p", "720p", "1080p"])

bg_files = st.file_uploader(
    "Upload Background Image/Video (opsional, bisa lebih dari 1)", 
    type=["jpg","png","mp4","mov"], accept_multiple_files=True
)
effect_files = st.file_uploader(
    "Upload Efek Suara Tambahan (opsional, mp3/wav)", 
    type=["mp3","wav"], accept_multiple_files=True
)

text_fade_duration = st.slider("Durasi fade-in/out teks tiap baris (detik)", 1, 5, 2)
preview_duration = st.slider("Durasi Preview (detik)", 5, 15, 5)

# --- Fungsi bantu ---
def generate_tts_audio(text, voice_choice):
    tld_map = {"Wanita":"com","Pria":"co.uk"}
    tts = gTTS(text, lang='id', tld=tld_map[voice_choice])
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def pil_to_np(img):
    return np.array(img)

def create_text_clip(line, font, fade_duration, dur_per_line):
    txt_img = Image.new("RGBA", (720,480), (0,0,0,0))
    draw = ImageDraw.Draw(txt_img)
    draw.text((20,20), line, font=font, fill=(255,255,255))
    txt_array = pil_to_np(txt_img)
    clip = ImageClip(txt_array).set_duration(dur_per_line).fadein(fade_duration).fadeout(fade_duration)
    return clip

# --- Preview Mode ---
if st.button("Update Preview"):
    if not narasi.strip():
        st.warning("Harap masukkan deskripsi dulu!")
    else:
        with st.spinner("Membuat preview video... ⏳"):
            # Audio
            audio_file = generate_tts_audio(narasi, voice)
            audio_clip = AudioFileClip(audio_file).set_duration(preview_duration)

            if effect_files:
                from moviepy.audio.AudioClip import CompositeAudioClip
                effect_clips = [AudioFileClip(ef.name).set_duration(preview_duration) for ef in effect_files]
                audio_clip = CompositeAudioClip([audio_clip] + effect_clips)

            # Background video/image
            clips = []
            if bg_files:
                dur_per_clip = preview_duration / len(bg_files)
                for f in bg_files:
                    ext = f.name.split(".")[-1].lower()
                    if ext in ["mp4","mov"]:
                        clip = VideoFileClip(f.name).subclip(0, min(dur_per_clip, VideoFileClip(f.name).duration))
                    else:
                        img = Image.open(f)
                        clip = ImageClip(pil_to_np(img)).set_duration(dur_per_clip).resize(height=480)
                    clips.append(clip)
                video_clip = concatenate_videoclips(clips, method="compose")
            else:
                video_clip = ColorClip(size=(720,480), color=(0,0,0), duration=preview_duration)

            # Text overlay
            lines = textwrap.wrap(narasi, width=40)
            font_size = 30
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            dur_per_line = preview_duration / max(len(lines),1)
            txt_clips = [create_text_clip(line, font, text_fade_duration, dur_per_line) for line in lines]
            text_overlay = CompositeVideoClip(txt_clips)

            # Merge
            preview_clip = CompositeVideoClip([video_clip, text_overlay])
            preview_clip = preview_clip.set_audio(audio_clip)

            # Save preview
            preview_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            preview_clip.write_videofile(preview_file.name, fps=24, codec="libx264", audio_codec="aac")
            st.success("✅ Preview siap ditinjau!")
            st.video(preview_file.name)

# --- Generate Final Video ---
if st.button("Generate Final Video"):
    st.info("Klik 'Update Preview' dulu untuk meninjau & menyetujui konten sebelum generate video final.")
