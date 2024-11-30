import assemblyai as aai
import streamlit as st
from dotenv import load_dotenv
import hashlib
import os
import io


# Set the style of the page
def page_setup():
    st.set_page_config(page_title="📜 Transcribe")
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        r"""
        <style>
        .stDeployButton {
                visibility: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Set page state
def init_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""


# Transcribe audia using assemblyai API
def transcription(audio_file, options):
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
            res += f"**{speaker_tag} {utterance.speaker}**: {utterance.text}\n\n\n"
    st.session_state.transcript = res


# Verify the password
def check_password(password, hash_value):
    return hashlib.md5(password.encode()).hexdigest() == hash_value


def render_login_page():
    st.title("Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if check_password(password, PASSWORD_HASH):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")


def render_main_page():
    # Main page
    st.title("📜✍️ Interview Transcriber")

    st.subheader("Upload your audio file")
    # File upload
    audio_file = st.file_uploader(" ", type=["mp3", "wav", "m4a"])

    st.markdown("# ")

    # Transcription options
    st.subheader("Transcription Options")
    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
    lang = {"de": "German", "en": "English"}

    language = col1.selectbox(
        "Language", options=list(lang.keys()), format_func=lambda x: lang[x]
    )

    speaker_recognition = col2.checkbox("Speaker recognition")

    # Transcription button
    transcribe = col3.button("Transcribe", use_container_width=True)

    if transcribe and audio_file is not None:
        # Dummy transcription call
        options = {"language": language, "speaker_recognition": speaker_recognition}
        with st.spinner("Transcribing..."):
            transcription(audio_file, options)
        st.success("Transcription Complete!")
    elif transcribe:
        st.warning("Please upload an audio file before transcribing.")

    # show transcription and download button
    if st.session_state.transcript != "":
        # Display transcribed text
        st.markdown("---")
        st.markdown(st.session_state.transcript, unsafe_allow_html=True)

        # Download transcribed text
        txt_name = ".".join(audio_file.name.split(".")[:-1]) + ".txt"
        st.download_button(
            label="Download Transcription",
            data=st.session_state.transcript,
            file_name=txt_name,
            mime="text/plain",
        )


# Main page display function
def render():
    if not st.session_state.authenticated:
        render_login_page()
    else:
        render_main_page()


if __name__ == "__main__":
    # Get credentials
    load_dotenv()
    PASSWORD_HASH = hashlib.md5(os.getenv("USER_PW").encode()).hexdigest()
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    # Set the style of the page
    page_setup()

    # Set page state
    init_state()

    # display page
    render()
