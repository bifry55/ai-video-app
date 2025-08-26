import streamlit as st
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import textwrap, tempfile, os

st.set_page_config(page_title="AI Video Ultimate Cinematic Pro", layout="centered")
st.title("🎬 AI Video Ultimate Cinematic Pro")

# --- Input User ---
narasi = st.text_area("Masukkan Deskripsi / LP", height=150)
voice = st.radio("Pilihan Suara", ["Wanita", "Pria"])
durasi = st.slider("Durasi Video Total (detik)", 5, 120, 20)

bg_files = st.file_uploader(
    "Upload background image/video (opsional, bisa lebih dari 1)", 
    type=["jpg","png","mp4","mov"], accept_multiple_files=True
)

effect_files = st.file_uploader(
    "Upload efek suara tambahan (opsional, mp3/wav)", 
    type=["mp3","wav"], accept_multiple_files=True
)

highlight_words = st.text_input("Highlight kata kunci (pisahkan koma)", "")

text_fade_duration = st.slider("Durasi fade-in/out teks tiap baris (detik)", 1, 5, 2)
filter_choice = st.selectbox("Filter warna cinematic", ["None", "Classic", "Warm", "Cool", "Dramatic"])

if st.button("Generate Ultimate Video"):
    if not narasi.strip():
        st.warning("Harap masukkan deskripsi dulu!")
    else:
        with st.spinner("Membuat video cinematic... ⏳"):

            # --- 1. Audio Narasi ---
            tld_map = {"Wanita":"com","Pria":"co.uk"}
            tts = gTTS(narasi, lang='id', tld=tld_map[voice])
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(audio_temp.name)
            audio_clip = AudioFileClip(audio_temp.name).set_duration(durasi)

            # --- 2. Efek suara tambahan ---
            if effect_files:
                from moviepy.audio.AudioClip import CompositeAudioClip
                effect_clips = [AudioFileClip(ef.name).set_duration(durasi) for ef in effect_files]
                audio_clip = CompositeAudioClip([audio_clip] + effect_clips)

            # --- 3. Background Video / Image Ken Burns effect ---
            clips = []
            if bg_files:
                dur_per_clip = durasi / len(bg_files)
                for f in bg_files:
                    ext = f.name.split(".")[-1].lower()
                    if ext in ["mp4","mov"]:
                        clip = VideoFileClip(f.name).subclip(0, min(dur_per_clip, VideoFileClip(f.name).duration))
                    else:
                        img = Image.open(f)
                        clip = ImageClip(img).set_duration(dur_per_clip).resize(height=480)
                        clip = clip.fx(vfx.zoom_in, final_scale=1.1)
                    clips.append(clip)
                video_clip = concatenate_videoclips(clips, method="compose")
            else:
                video_clip = ColorClip(size=(720,480), color=(0,0,0), duration=durasi)

            # --- 4. Teks Animasi ---
            lines = textwrap.wrap(narasi, width=40)
            font_size = 30
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            txt_clips = []
            dur_per_line = durasi / max(len(lines),1)
            highlights = [w.strip() for w in highlight_words.split(",") if w.strip()]

            for i, line in enumerate(lines):
                txt_img = Image.new("RGBA", (720,480), (0,0,0,0))
                draw = ImageDraw.Draw(txt_img)
                if highlights:
                    for word in highlights:
                        line = line.replace(word, f"{word}")  # bisa ganti styling
                draw.text((20,20), line, font=font, fill=(255,255,255))
                clip = ImageClip(txt_img).set_duration(dur_per_line).fadein(text_fade_duration).fadeout(text_fade_duration).set_start(i*dur_per_line)
                txt_clips.append(clip)
            text_overlay = CompositeVideoClip(txt_clips)

            # --- 5. Filter warna cinematic ---
            if filter_choice != "None":
                # Simple color filter example
                def color_filter(get_frame, factor):
                    import numpy as np
                    frame = get_frame().astype(np.float32)
                    if factor == "Classic":
                        frame[:,:,0] *= 1.0; frame[:,:,1]*=0.95; frame[:,:,2]*=0.9
                    elif factor == "Warm":
                        frame[:,:,0] *= 1.1; frame[:,:,1]*=1.0; frame[:,:,2]*=0.9
                    elif factor == "Cool":
                        frame[:,:,0] *= 0.9; frame[:,:,1]*=0.95; frame[:,:,2]*=1.1
                    elif factor == "Dramatic":
                        frame = np.clip(frame*1.2,0,255)
                    return frame.astype(np.uint8)
                video_clip = video_clip.fl_image(lambda frame: color_filter(lambda: frame, filter_choice))

            # --- 6. Merge Video + Text + Audio ---
            final_clip = CompositeVideoClip([video_clip, text_overlay])
            final_clip = final_clip.set_audio(audio_clip)

            # --- 7. Simpan video sementara ---
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            final_clip.write_videofile(output_file.name, fps=24, codec="libx264", audio_codec="aac")

            # --- 8. Tampilkan & Download ---
            st.success("✅ Video cinematic ultimate selesai!")
            st.video(output_file.name)
            with open(output_file.name,"rb") as f:
                st.download_button("📥 Download Video", f, file_name="ultimate_cinematic.mp4", mime="video/mp4")
