import assemblyai as aai
import streamlit as st
from dotenv import load_dotenv
import hashlib
import os
import io

# Constants for speaker tags
SPEAKER_TAG = {"en": "Speaker", "de": "Sprecher"}

def setup_page():
    """Set up the Streamlit page configuration and styling."""
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


def initialize_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""


def transcribe_audio(audio_file, options):
    """
    Transcribe audio using AssemblyAI API.

    Args:
        audio_file: The uploaded audio file.
        options: Dictionary containing transcription options (language and speaker recognition).

    Returns:
        str: Transcribed text or error message.
    """
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

    try:
        transcript = transcriber.transcribe(audio_bytes)
        if transcript.status == aai.TranscriptStatus.error:
            return transcript.error

        speaker_tag = SPEAKER_TAG[options["language"]]
        result = transcript.text

        if options["speaker_recognition"]:
            result = ""
            for utterance in transcript.utterances:
                result += f"**{speaker_tag} {utterance.speaker}**: {utterance.text}\n\n\n"

        st.session_state.transcript = result
    except Exception as e:
        return str(e)


def verify_password(password, hash_value):
    """Verify if the provided password matches the stored hash."""
    return hashlib.md5(password.encode()).hexdigest() == hash_value


def render_login_page():
    """Render the login page with a password input field."""
    st.title("Login")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if verify_password(password, PASSWORD_HASH):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")


def render_main_page():
    """Render the main application page with transcription functionality."""
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
            error_message = transcribe_audio(audio_file, options)
            if error_message:
                st.error(error_message)
            else:
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


def render():
    """Render the appropriate page based on authentication state."""
    if not st.session_state.authenticated:
        render_login_page()
    else:
        render_main_page()


if __name__ == "__main__":
    # Get credentials
    load_dotenv()
    PASSWORD_HASH = hashlib.md5(os.getenv("USER_PW").encode()).hexdigest()
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    # Set up the page and initialize state
    setup_page()
    initialize_state()

    # Display the appropriate page
    render()
