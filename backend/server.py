# gateway.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from doc_image import app as app_docs    # your existing document app
from main import app as app_video   # your existing video app
from coversation import app as app_conversation  # your existing conversation app
from weather import app as app_weather  # your existing weather app
from speechTospeech import app as app_speech  # your existing speech-to-speech app
from textToSpeech import app as app_texttoSpeech  # your existing text-to-speech app

app = FastAPI(title="Unified API Gateway")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the two apps
app.mount("/document", app_docs)       # accessible at /document/*
app.mount("/translate", app_video)    # accessible at /translate/*
app.mount("/conversation", app_conversation)  # accessible at /conversation/*
app.mount("/weather", app_weather)  # accessible at /weather/*
app.mount("/speech", app_speech)  # accessible at /speech/*
app.mount("/tts", app_texttoSpeech)  # accessible at /text-to-speech/*

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
