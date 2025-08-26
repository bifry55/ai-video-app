import streamlit as st
import tempfile
import os
from pathlib import Path
from moviepy.editor import *
from google.cloud import texttospeech
import numpy as np

# -------------------------------
# Config AI Studio Google TTS
# -------------------------------
st.set_page_config(page_title="Ultimate AI Video Editor", layout="wide")

# Setup Google TTS client
# Pastikan sudah buat service account dan download JSON credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
tts_client = texttospeech.TextToSpeechClient()

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("Ultimate AI Video Editor – 4 Angle")

# Input Deskripsi LP
deskripsi = st.text_area("Masukkan Deskripsi / Copy-Paste LP", height=150)

# Pilihan Resolusi
resolusi = st.selectbox("Pilih Resolusi Video", ["480p", "720p", "1080p"])
res_map = {"480p": (854,480), "720p": (1280,720), "1080p": (1920,1080)}

# Pilihan Suara AI Studio Google
suara_preset = ["id-ID-Wavenet-F", "id-ID-Wavenet-M"] # contoh preset default wanita/pria
voice_choice = st.selectbox("Pilih Suara Narasi (AI Studio Google)", suara_preset)

# Tombol Generate Script 4 Angle
if st.button("Generate Script 4 Angle"):
    if not deskripsi.strip():
        st.warning("Isi deskripsi dulu!")
    else:
        st.session_state["scripts"] = {}
        angles = ["FOMO", "Benefit", "Problem-Solution", "Testimonial"]
        for angle in angles:
            # Dummy AI scene generation (nanti bisa diganti AI sesungguhnya)
            scenes = [
                f"{angle} Scene 1: {deskripsi[:50]}...",
                f"{angle} Scene 2: {deskripsi[50:100]}...",
                f"{angle} Scene 3: {deskripsi[100:150]}..."
            ]
            st.session_state["scripts"][angle] = scenes
        st.success("Script 4 angle berhasil dibuat!")

# Preview + Edit per Scene
if "scripts" in st.session_state:
    final_videos = []
    for angle, scenes in st.session_state["scripts"].items():
        with st.expander(f"Preview & Edit {angle} Angle"):
            edited_scenes = []
            for i, scene in enumerate(scenes):
                text = st.text_area(f"{angle} - Scene {i+1}", value=scene, key=f"{angle}_{i}")
                edited_scenes.append(text)
            st.session_state["scripts"][angle] = edited_scenes
            if st.button(f"Preview {angle}", key=f"preview_{angle}"):
                clips = []
                for s in edited_scenes:
                    # Generate TTS via Google TTS
                    synthesis_input = texttospeech.SynthesisInput(text=s)
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="id-ID", name=voice_choice
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                    response = tts_client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                    # Simpan audio sementara
                    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    audio_file.write(response.audio_content)
                    audio_file.close()
                    audio_clip = AudioFileClip(audio_file.name)
                    # Text overlay dummy
                    txt_clip = TextClip(s, fontsize=30, color='white', size=res_map[resolusi], method='caption').set_duration(audio_clip.duration)
                    txt_clip = txt_clip.set_audio(audio_clip)
                    clips.append(txt_clip)
                preview_clip = concatenate_videoclips(clips, method="compose")
                preview_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                preview_clip.write_videofile(preview_file.name, fps=24)
                st.video(preview_file.name)
                # Simpan untuk generate final
                st.session_state.setdefault("final_clips", {})[angle] = clips

# Generate Final Video
if "final_clips" in st.session_state and st.button("Generate Final 4 Videos"):
    st.success("Generating final videos with AI overlay effects...")
    for angle, clips in st.session_state["final_clips"].items():
        # Tambahkan efek overlay AI (dummy)
        final_clips = []
        for clip in clips:
            # Misal fadein/fadeout + watermark
            clip = clip.fadein(0.5).fadeout(0.5)
            final_clips.append(clip)
        final_video = concatenate_videoclips(final_clips, method="compose")
        output_file = Path(f"{angle}_Final.mp4")
        final_video.write_videofile(str(output_file), fps=24)
        st.video(str(output_file))
        st.success(f"{angle} video generated!")
