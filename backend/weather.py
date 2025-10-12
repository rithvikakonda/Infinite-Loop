from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import requests
from datetime import datetime
import re
from groq import Groq

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------
# Config
# ---------------------------

API_CONFIG = {
    "en": {"NAME": "English", "CODE": "en", "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"},
    "te": {"NAME": "Telugu (తెలుగు)", "CODE": "te", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "hi": {"NAME": "Hindi (हिंदी)", "CODE": "hi", "ASR_SERVICE": "ai4bharat/conformer-hi-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
}

BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"
GROQ_API_KEY = "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"

# ---------------------------
# Helper functions (ASR, MT, TTS, Weather, AI)
# ---------------------------

def asr(audio_file_path, lang):
    config = API_CONFIG[lang]
    with open(audio_file_path, "rb") as f:
        audio_content = base64.b64encode(f.read()).decode("utf-8")

    headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
    payload = {
        "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": config["CODE"]}, "serviceId": config["ASR_SERVICE"], "audioFormat": "wav", "samplingRate": 16000}}],
        "inputData": {"audio": [{"audioContent": audio_content}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["source"]
    else:
        raise Exception(f"ASR failed: {result}")

def mt(text, source_lang, target_lang):
    if source_lang == target_lang:
        return text
    source_code = API_CONFIG[source_lang]["CODE"]
    target_code = API_CONFIG[target_lang]["CODE"]
    headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
    payload = {
        "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_code, "targetLanguage": target_code}, "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4", "numTranslation": "True"}}],
        "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
    }
    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["target"]
    else:
        raise Exception(f"MT failed: {result}")

def tts(text, lang, gender="female"):
    config = API_CONFIG[lang]
    headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
    payload = {
        "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": config["CODE"]}, "serviceId": config["TTS_SERVICE"], "gender": gender, "samplingRate": 8000}}],
        "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
    }
    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
        filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(audio_content))
        return filename
    else:
        raise Exception(f"TTS failed: {result}")

def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None):
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not set")
    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful agricultural advisor."},
            {"role": "user", "content": query_text}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=300
    )
    return chat_completion.choices[0].message.content

def handle_farmer_query_pipeline(audio_file_path, farmer_lang="te", gender="female", lat=None, lon=None):
    recognized_text = asr(audio_file_path, farmer_lang)
    text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
    ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
    answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    audio_filename = tts(answer_local, farmer_lang, gender)
    return {
        "success": True,
        "query_text": recognized_text,
        "answer_text": answer_local,
        "audio_url": audio_filename
    }

# ---------------------------
# Routes
# ---------------------------

@app.post("/handle_farmer_query")
async def handle_query(
    file: UploadFile = File(...),
    lang: str = Form("te"),
    gender: str = Form("female"),
    lat: float = Form(None),
    lon: float = Form(None)
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    try:
        result = handle_farmer_query_pipeline(file_path, farmer_lang=lang, gender=gender, lat=lat, lon=lon)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("  {filename}")
def serve_audio(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="File not found")

# @app.get("outputs/{filename}")
# def serve_audio(filename: str):
#     file_path = os.path.join(OUTPUT_FOLDER, filename)
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="audio/wav")
#     else:
#         raise HTTPException(status_code=404, detail="File not found")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)