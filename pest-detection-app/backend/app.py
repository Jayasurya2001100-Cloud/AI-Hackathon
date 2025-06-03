from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import azure.cognitiveservices.speech as speechsdk
import tempfile
import io
import os
from pydantic import BaseModel
import httpx

from predict import predict  # ensure model is loaded once in predict.py
from dotenv import load_dotenv
load_dotenv()

# Use environment variables in production for safety
AZURE_SPEECH_KEY = "5YiHGkl9cDVsW2Xql6rYaYvrDTyaILfILgbR8Gvu0oi6CZ4kmtBAJQQJ99BEACYeBjFXJ3w3AAAYACOGAT1d"
AZURE_REGION = "eastus"

# FastAPI instance
app = FastAPI(title="Pest Detection API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Speech Config (shared)
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)


@app.post("/predict-image/")
async def predict_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    image_bytes = await file.read()
    prediction_result = predict(image_bytes)  # Assuming it returns dict with pest & confidence

    pest = prediction_result.get("pest", "Unknown")
    confidence = prediction_result.get("confidence", 0.0)
    confidence_percent = round(confidence * 100, 2)

    return {
        "pest_detected": pest,
        "confidence_score": f"{confidence_percent}%",
        "message": f"The image is most likely to contain {pest} pest."
    }

class TranslationRequest(BaseModel):
    text: str
    to_language: str

@app.post("/translate/")
async def translate(request: TranslationRequest):
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={request.to_language}"

    headers = {
        "Ocp-Apim-Subscription-Key": "3kXjOXV1wPWlHf31gF9RJmAb7QGYnjcv5EH6LVb6ZEXoj98Lc1TpJQQJ99BFACYeBjFXJ3w3AAAbACOGi7dt",
        "Ocp-Apim-Subscription-Region": "eastus",
        "Content-Type": "application/json"
    }

    body = [{"Text": request.text}]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            translation = response.json()[0]['translations'][0]['text']
            return {"translated_text": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speech-to-text/")
async def speech_to_text(file: UploadFile = File(...), language: str = Query("en-US")):
    try:
        audio_bytes = await file.read()

        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio.flush()

            speech_config.speech_recognition_language = language
            audio_input = speechsdk.AudioConfig(filename=temp_audio.name)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_input
            )

            result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {"text": result.text}
        else:
            return {"error": "Speech not recognized", "reason": result.reason.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text error: {str(e)}")


@app.post("/text-to-speech/")
async def text_to_speech(text: str = Query(...), language: str = Query("en-US")):
    try:
        speech_config.speech_synthesis_language = language
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data
            return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")
        else:
            return {"error": "Speech synthesis failed", "reason": result.reason.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech error: {str(e)}")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}
