
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
import os
import tempfile
from src.alignment import align_audio_lyrics
from src.segmentation import segment_results, save_to_srt, subtitles_to_ass_string

st.set_page_config(page_title="Subtitle Generator", page_icon="icon.svg")

st.title("Auto Subtitle Generator")
st.markdown("Create synchronized subtitles (SRT) from Audio + Lyrics text using AI.")

# Sidebar configuration
st.sidebar.header("Configuration")
model_type = st.sidebar.selectbox(
    "AI Model",
    options=["tiny", "base", "small", "medium", "large"],
    index=1,
    help="Select 'base' for speed, 'small'/'medium' for better accuracy."
)

max_len = st.sidebar.number_input(
    "Max Characters per Line",
    min_value=10,
    max_value=100,
    value=30,
    step=1,
    help="Maximum length of a subtitle line before splitting."
)

language = st.sidebar.text_input("Language Code", value="vi", help="e.g., 'vi', 'en', 'ja'")

export_format = st.sidebar.selectbox(
    "Export Format",
    options=["SRT", "ASS", "Both"],
    index=0,
    help="Select the format for the generated subtitles."
)

# Main interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Audio")
    audio_file = st.file_uploader("Upload MP3, WAV, etc.", type=["mp3", "wav", "m4a", "flac"])

with col2:
    st.subheader("2. Upload Lyrics")
    lyrics_file = st.file_uploader("Upload Lyrics (.txt)", type=["txt"])

if audio_file and lyrics_file:
    st.audio(audio_file)
    
    # Read lyrics content
    try:
        lyrics_text = lyrics_file.read().decode("utf-8")
        st.text_area("Lyrics Preview:", value=lyrics_text, height=150)
    except Exception as e:
        st.error(f"Error reading lyrics file. Make sure it is UTF-8 encoded. Detail: {e}")
        st.stop()
        
    if st.button("Generate Subtitles", type="primary"):
        with st.spinner(f"Aligning audio with model '{model_type}'... This may take a while."):
            try:
                # Save uploaded audio to a temp file because stable-ts needs a file path
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_audio:
                    tmp_audio.write(audio_file.getvalue())
                    tmp_audio_path = tmp_audio.name
                
                # Align
                result = align_audio_lyrics(tmp_audio_path, lyrics_text, language=language, model_name=model_type)
                
                # Segment
                subtitles = segment_results(result, lyrics_text, max_chars=max_len)
                
                # Generate SRT string
                def subtitles_to_srt_string(subs):
                    output = ""
                    def format_timestamp(seconds):
                        hours = int(seconds // 3600)
                        minutes = int((seconds % 3600) // 60)
                        secs = int(seconds % 60)
                        millis = int((seconds - int(seconds)) * 1000)
                        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

                    for i, sub in enumerate(subs, 1):
                        output += f"{i}\n"
                        output += f"{format_timestamp(sub['start'])} --> {format_timestamp(sub['end'])}\n"
                        output += f"{sub['text']}\n\n"
                    return output

                srt_content = subtitles_to_srt_string(subtitles)
                ass_content = subtitles_to_ass_string(subtitles)
                
                st.success("Analysis Complete!")
                
                base_filename = os.path.splitext(audio_file.name)[0]
                
                # Display result based on format
                if export_format == "SRT":
                    st.text_area("Generated Subtitles (SRT):", value=srt_content, height=300)
                    st.download_button(
                        label="Download .SRT File",
                        data=srt_content,
                        file_name=base_filename + ".srt",
                        mime="text/plain"
                    )
                elif export_format == "ASS":
                    st.text_area("Generated Subtitles (ASS):", value=ass_content, height=300)
                    st.download_button(
                        label="Download .ASS File",
                        data=ass_content,
                        file_name=base_filename + ".ass",
                        mime="text/plain"
                    )
                else: # Both
                    tab1, tab2 = st.tabs(["SRT Subtitles", "ASS Subtitles"])
                    with tab1:
                        st.text_area("Generated Subtitles (SRT):", value=srt_content, height=300, key="srt_preview")
                        st.download_button(
                            label="Download .SRT File",
                            data=srt_content,
                            file_name=base_filename + ".srt",
                            mime="text/plain",
                            key="srt_download"
                        )
                    with tab2:
                        st.text_area("Generated Subtitles (ASS):", value=ass_content, height=300, key="ass_preview")
                        st.download_button(
                            label="Download .ASS File",
                            data=ass_content,
                            file_name=base_filename + ".ass",
                            mime="text/plain",
                            key="ass_download"
                        )
                
                # Cleanup temp file
                os.remove(tmp_audio_path)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                if 'tmp_audio_path' in locals() and os.path.exists(tmp_audio_path):
                     os.remove(tmp_audio_path)
