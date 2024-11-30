import assemblyai as aai
import streamlit as st
from dotenv import load_dotenv
import hashlib
import os
import io

load_dotenv()
PASSWORD_HASH = hashlib.md5(os.getenv("USER_PW").encode()).hexdigest()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


# Dummy transcription function
def transcription(audio_file, options):

    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,
        language_code=options["language"],
        speaker_labels=options["speaker_recognition"],
    )
    transcriber = aai.Transcriber(config=config)

    # Convert uploaded file to BytesIO
    audio_bytes = io.BytesIO(audio_file.getvalue())
    audio_bytes.name = audio_file.name
    audio_bytes.seek(0)

    transcript = transcriber.transcribe(audio_bytes)

    if transcript.status == aai.TranscriptStatus.error:
        return transcript.error
    speaker_tag = {"en": "Speaker", "de": "Sprecher"}[options["language"]]
    res = transcript.text
    if options["speaker_recognition"]:
        res = ""
        for utterance in transcript.utterances:
            res += f"**{speaker_tag} {utterance.speaker}**: {utterance.text}\n<br><br>"
    return res


# Function to verify the password
def check_password(password, hash_value):
    return hashlib.md5(password.encode()).hexdigest() == hash_value


# Password-protected entry
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if check_password(password, PASSWORD_HASH):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
else:
    # Main page
    st.title("Audio Transcription App")
    st.write("Upload an audio file, configure options, and transcribe.")

    # File upload
    audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav", "m4a"])

    # Transcription options
    st.subheader("Transcription Options")
    lang = {"de": "German", "en": "English"}

    language = st.selectbox(
        "Language", options=list(lang.keys()), format_func=lambda x: lang[x]
    )
    speaker_recognition = st.checkbox("Enable speaker recognition")

    # Transcription button
    transcribe = st.button("Transcribe")
    if transcribe and audio_file is not None:
        # Dummy transcription call
        options = {"language": language, "speaker_recognition": speaker_recognition}
        with st.spinner("Transcribing..."):
            transcribed_text = transcription(audio_file, options)
        st.success("Transcription Complete!")

        # Display transcribed text
        # st.text_area("Transcribed Text", transcribed_text, height=200)
        st.markdown("---")
        st.markdown(transcribed_text, unsafe_allow_html=True)

        # Download transcribed text
        txt_name = ".".join(audio_file.name.split(".")[:-1]) + ".txt"
        st.download_button(
            label="Download Transcription",
            data=transcribed_text,
            file_name=txt_name,
            mime="text/plain",
        )
    elif transcribe:
        st.warning("Please upload an audio file before transcribing.")
