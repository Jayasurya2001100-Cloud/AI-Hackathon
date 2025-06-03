import streamlit as st
from PIL import Image
import requests
import azure.cognitiveservices.speech as speechsdk
import openai
import io


# --- Azure OpenAI config ---
AZURE_OPENAI_API_KEY = "52eSzqiaUyV3wDiXH3qx6ITFrVC6AcFPm9m17Ka9uRcQ4qQudYe1JQQJ99BCACYeBjFXJ3w3AAABACOG4H6h"
AZURE_OPENAI_ENDPOINT = "https://dsopenai007.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o-mini"
AZURE_OPENAI_API_VERSION = "2024-08-01-preview"

# --- Azure Translator config ---
AZURE_TRANSLATOR_KEY = "3kXjOXV1wPWlHf31gF9RJmAb7QGYnjcv5EH6LVb6ZEXoj98Lc1TpJQQJ99BFACYeBjFXJ3w3AAAbACOGi7dt"
AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
BACKEND_URL = "http://127.0.0.1:8000/predict-image/"

# --- Azure Speech Service config ---
AZURE_SPEECH_KEY = "5YiHGkl9cDVsW2Xql6rYaYvrDTyaILfILgbR8Gvu0oi6CZ4kmtBAJQQJ99BEACYeBjFXJ3w3AAAYACOGAT1d"
AZURE_SERVICE_REGION = "eastus"  # Use the region where your Azure Speech service is deployed
# --- OpenAI client setup ---
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_OPENAI_API_VERSION

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Pest Detection with Voice & AI", layout="centered")
st.title("🌿 GreenGuard AI - Pest Detection Made Easy")
st.markdown("Upload a pest-affected plant image or use voice commands to detect pests and chat about farming.")

language = st.selectbox("🌐 Select your preferred language", ["English", "Tamil", "Hindi", "Kannada", "Telugu", "Malayalam"])
LANG_CODE_MAP = {"English": "en", "Tamil": "ta", "Hindi": "hi", "Kannada": "kn", "Telugu": "te", "Malayalam": "ml"}
VOICE_MAP = {
    "English": "en-US-JennyNeural",
    "Tamil": "ta-IN-PriyaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Kannada": "kn-IN-GaganNeural",
    "Telugu": "te-IN-SwaraNeural",
    "Malayalam": "ml-IN-PrabhaNeural"
}

# --- Speech to Text ---
def azure_speech_to_text():
    try:
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        st.info("🎧 Listening... Speak now.")
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            st.success(f"🗣 You said: {result.text}")
            return result.text
        else:
            st.error("❗ Speech recognition failed or no speech detected.")
            return None
    except Exception as e:
        st.error(f"Speech recognition error: {e}")
        return None

# --- Translation ---
def translate_text(text, to_lang):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_SERVICE_REGION,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]
    try:
        response = requests.post(AZURE_TRANSLATOR_ENDPOINT, params={"to": to_lang}, headers=headers, json=body)
        response.raise_for_status()
        return response.json()[0]["translations"][0]["text"]
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

def translate_response(text, lang):
    prefixes = {
        "Tamil": "உங்கள் பதில்: ",
        "Hindi": "आपका उत्तर: ",
        "Kannada": "ನಿಮ್ಮ ಉತ್ತರ: ",
        "Telugu": "మీ సమాధానం: ",
        "Malayalam": "നിങ്ങളുടെ ഉത്തരമാണ്: "
    }
    return prefixes.get(lang, "") + text

# --- OpenAI API Calls ---
def get_pest_insight(pest_name):
    prompt = f"""
You are a plant pathology expert.  
Provide a brief overview of the pest or disease '{pest_name}', including:  
1. Description  
2. Symptoms  
3. Treatments or prevention methods  
Keep the response short and clear.
"""
    try:
        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful agricultural expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error getting insights: {e}"

def get_chat_response(pest_info, user_question):
    prompt = f"""
You are a knowledgeable agricultural assistant. Here is the detected pest info: {pest_info}

Answer the farmer's question clearly and helpfully:
{user_question}
"""
    try:
        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful agricultural assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error getting chat response: {e}"

# --- Speech synthesis config (unified region) ---
def get_speech_config(lang: str):
    voice = VOICE_MAP.get(lang, VOICE_MAP["English"])
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)
    speech_config.speech_synthesis_voice_name = voice
    return speech_config

# --- Azure TTS for Streamlit ---
def azure_text_to_speech_streamlit(text: str, lang: str):
    try:
        speech_config = get_speech_config(lang)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # result.audio_data is bytes
            audio_bytes = result.audio_data
            audio_buffer = io.BytesIO(audio_bytes)
            st.audio(audio_buffer.read(), format="audio/wav")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            st.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancellation_details.error_details}")
        else:
            st.error(f"Speech synthesis failed with reason: {result.reason}")
    except Exception as e:
        st.error(f"Speech synthesis exception: {e}")

# --- Image Prediction ---
def predict_image(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(BACKEND_URL, files=files)
        if response.status_code == 200:
            data = response.json()
            pest = data.get("pest_detected", "Unknown")
            confidence_str = data.get("confidence_score", "0.0%").replace("%", "")
            confidence = float(confidence_str)

            st.success(f"✅ Pest Detected: **{pest}** | 🎯 Confidence: **{confidence:.2f}%**")

            insight_english = get_pest_insight(pest)

            if language != "English":
                translated = translate_text(insight_english, LANG_CODE_MAP[language])
                final_text = translate_response(translated, language)
            else:
                final_text = insight_english

            st.markdown("### 🌱 Pest Insight & Prescription")
            st.markdown(final_text, unsafe_allow_html=True)

            azure_text_to_speech_streamlit(final_text, language)

            # Save pest insight for chat context (always English for consistency)
            st.session_state["pest_info"] = insight_english
        else:
            st.error(f"❌ API Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"❗ Exception: {e}")

# --- Main UI ---

uploaded_file = st.file_uploader("📁 Upload Pest Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="🖼 Uploaded Image", use_column_width=True)
    if st.button("🔍 Analyze Image"):
        predict_image(uploaded_file)

# Initialize pest_info if not in session state
if "pest_info" not in st.session_state:
    st.session_state["pest_info"] = "No pest information available yet."

# Chat section
st.markdown("---")
st.header("💬 Ask your farming questions")

if st.button("🎙 Use Voice to Ask"):
    question = azure_speech_to_text()
else:
    question = st.text_input("Enter your question here:")

if question:
    with st.spinner("🧠 Thinking..."):
        chat_reply = get_chat_response(st.session_state["pest_info"], question)

        # Translate response if needed
        if language != "English":
            chat_reply_translated = translate_text(chat_reply, LANG_CODE_MAP[language])
            chat_reply_display = translate_response(chat_reply_translated, language)
        else:
            chat_reply_display = chat_reply

        st.markdown(f"**Assistant:** {chat_reply_display}")
        azure_text_to_speech_streamlit(chat_reply_display, language)
