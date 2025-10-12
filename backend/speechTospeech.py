# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import requests
# import os
# from datetime import datetime
# from groq import Groq
# import re
# import base64
# import tempfile
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Config: Language-specific settings
# # ---------------------------

# API_CONFIG = {
#     "en": {
#         "NAME": "English",
#         "CODE": "en",
#         "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4",
#         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"
#     },
#     "te": {
#         "NAME": "Telugu (తెలుగు)",
#         "CODE": "te",
#         "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4",
#         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"
#     },
#     "hi": {
#         "NAME": "Hindi (हिंदी)",
#         "CODE": "hi",
#         "ASR_SERVICE": "ai4bharat/conformer-hi-gpu--t4",
#         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
#     },
# }

# # Bhashini Configuration
# BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
# BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# # Create temp directory for audio files
# UPLOAD_FOLDER = tempfile.mkdtemp()
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# def asr(audio_file_path, lang):
#     """Call Bhashini ASR API for selected language"""
#     config = API_CONFIG[lang]
    
#     with open(audio_file_path, "rb") as audio_file:
#         audio_content = base64.b64encode(audio_file.read()).decode('utf-8')
    
#     headers = {
#         "Authorization": BHASHINI_AUTH_KEY,
#         "Content-Type": "application/json"
#     }
    
#     payload = {
#         "pipelineTasks": [
#             {
#                 "taskType": "asr",
#                 "config": {
#                     "language": {
#                         "sourceLanguage": config["CODE"]
#                     },
#                     "serviceId": config["ASR_SERVICE"],
#                     "audioFormat": "wav",
#                     "samplingRate": 16000
#                 }
#             }
#         ],
#         "inputData": {
#             "audio": [
#                 {
#                     "audioContent": audio_content
#                 }
#             ]
#         }
#     }
    
#     try:
#         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#         result = resp.json()
        
#         if resp.status_code == 200 and "pipelineResponse" in result:
#             recognized_text = result["pipelineResponse"][0]["output"][0]["source"]
#             return recognized_text
#         else:
#             raise Exception(f"Bhashini ASR failed: {result}")
#     except Exception as e:
#         raise Exception(f"ASR error: {str(e)}")


# def mt(text, source_lang, target_lang):
#     """Translate text using Bhashini API"""
#     if source_lang == target_lang:
#         return text
    
#     source_code = API_CONFIG[source_lang]["CODE"]
#     target_code = API_CONFIG[target_lang]["CODE"]
    
#     headers = {
#         "Authorization": BHASHINI_AUTH_KEY,
#         "Content-Type": "application/json"
#     }
    
#     payload = {
#         "pipelineTasks": [
#             {
#                 "taskType": "translation",
#                 "config": {
#                     "language": {
#                         "sourceLanguage": source_code,
#                         "targetLanguage": target_code
#                     },
#                     "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
#                     "numTranslation": "True"
#                 }
#             }
#         ],
#         "inputData": {
#             "input": [
#                 {
#                     "source": text
#                 }
#             ],
#             "audio": [
#                 {
#                     "audioContent": None
#                 }
#             ]
#         }
#     }
    
#     try:
#         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#         result = resp.json()
        
#         if resp.status_code == 200 and "pipelineResponse" in result:
#             translation_output = result["pipelineResponse"][0]["output"][0]["target"]
#             return translation_output
#         else:
#             raise Exception(f"Bhashini MT failed: {result}")
#     except Exception as e:
#         raise Exception(f"Translation error: {str(e)}")


# def tts(text, lang, gender="female"):
#     """Generate TTS audio using Bhashini API"""
#     config = API_CONFIG[lang]
    
#     headers = {
#         "Authorization": BHASHINI_AUTH_KEY,
#         "Content-Type": "application/json"
#     }
    
#     payload = {
#         "pipelineTasks": [
#             {
#                 "taskType": "tts",
#                 "config": {
#                     "language": {
#                         "sourceLanguage": config["CODE"]
#                     },
#                     "serviceId": config["TTS_SERVICE"],
#                     "gender": gender,
#                     "samplingRate": 8000
#                 }
#             }
#         ],
#         "inputData": {
#             "input": [
#                 {
#                     "source": text
#                 }
#             ],
#             "audio": [
#                 {
#                     "audioContent": None
#                 }
#             ]
#         }
#     }
    
#     try:
#         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#         result = resp.json()
        
#         if resp.status_code == 200 and "pipelineResponse" in result:
#             audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
            
#             output_filename = os.path.join(
#                 app.config['UPLOAD_FOLDER'],
#                 f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
#             )
#             with open(output_filename, "wb") as audio_file:
#                 audio_file.write(base64.b64decode(audio_content))
            
#             return output_filename
#         else:
#             raise Exception(f"Bhashini TTS failed: {result}")
#     except Exception as e:
#         raise Exception(f"TTS error: {str(e)}")


# @app.route('/api/languages', methods=['GET'])
# def get_languages():
#     """Return available languages"""
#     languages = [
#         {"code": key, "name": value["NAME"]}
#         for key, value in API_CONFIG.items()
#     ]
#     return jsonify({"languages": languages})


# @app.route('/api/translate-speech', methods=['POST'])
# def translate_speech():
#     """Main endpoint for speech-to-speech translation"""
#     try:
#         if 'audio' not in request.files:
#             return jsonify({"error": "No audio file provided"}), 400
        
#         audio_file = request.files['audio']
#         source_lang = request.form.get('source_lang', 'en')
#         target_lang = request.form.get('target_lang', 'hi')
#         gender = request.form.get('gender', 'female')
        
#         if audio_file.filename == '':
#             return jsonify({"error": "No selected file"}), 400
        
#         if source_lang not in API_CONFIG or target_lang not in API_CONFIG:
#             return jsonify({"error": "Invalid language selection"}), 400
        
#         # Save uploaded audio file
#         filename = secure_filename(audio_file.filename)
#         audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         audio_file.save(audio_path)
        
#         # Step 1: Speech to Text (ASR)
#         recognized_text = asr(audio_path, source_lang)
        
#         # Step 2: Translate Text
#         translated_text = mt(recognized_text, source_lang, target_lang)
        
#         # Step 3: Text to Speech (TTS)
#         output_audio_path = tts(translated_text, target_lang, gender)
        
#         # Clean up input file
#         os.remove(audio_path)
        
#         return jsonify({
#             "success": True,
#             "original_text": recognized_text,
#             "translated_text": translated_text,
#             "audio_file": os.path.basename(output_audio_path)
#         })
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/audio/<filename>', methods=['GET'])
# def get_audio(filename):
#     """Serve generated audio file"""
#     try:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
#         return send_file(file_path, mimetype='audio/wav')
#     except Exception as e:
#         return jsonify({"error": str(e)}), 404


# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({"status": "healthy", "message": "Speech Translation API is running"})


# # if __name__ == '__main__':
# #     app.run(debug=True, host='0.0.0.0', port=5000)

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import requests
import os
from datetime import datetime
import base64
import tempfile
from typing import Optional
from pydantic import BaseModel
from werkzeug.utils import secure_filename

# ---------------------------
# Initialize FastAPI
# ---------------------------
app = FastAPI(title="Speech Translation API (Bhashini-based)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Config: Language-specific settings
# ---------------------------
API_CONFIG = {
    "en": {
        "NAME": "English",
        "CODE": "en",
        "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4",
        "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"
    },
    "te": {
        "NAME": "Telugu (తెలుగు)",
        "CODE": "te",
        "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4",
        "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"
    },
    "hi": {
        "NAME": "Hindi (हिंदी)",
        "CODE": "hi",
        "ASR_SERVICE": "ai4bharat/conformer-hi-gpu--t4",
        "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
    },
}

BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# Temporary directory for files
UPLOAD_FOLDER = tempfile.mkdtemp()
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB


# ---------------------------
# Helper Functions
# ---------------------------

def asr(audio_file_path: str, lang: str) -> str:
    """Automatic Speech Recognition (ASR) using Bhashini"""
    config = API_CONFIG[lang]

    with open(audio_file_path, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode('utf-8')

    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {"sourceLanguage": config["CODE"]},
                    "serviceId": config["ASR_SERVICE"],
                    "audioFormat": "wav",
                    "samplingRate": 16000
                }
            }
        ],
        "inputData": {"audio": [{"audioContent": audio_content}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()

    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["source"]
    raise HTTPException(status_code=500, detail=f"ASR failed: {result}")


def mt(text: str, source_lang: str, target_lang: str) -> str:
    """Machine Translation (MT) using Bhashini"""
    if source_lang == target_lang:
        return text

    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": API_CONFIG[source_lang]["CODE"],
                        "targetLanguage": API_CONFIG[target_lang]["CODE"]
                    },
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                    "numTranslation": "True"
                }
            }
        ],
        "inputData": {"input": [{"source": text}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()

    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["target"]
    raise HTTPException(status_code=500, detail=f"Translation failed: {result}")


def tts(text: str, lang: str, gender: str = "female") -> str:
    """Text-to-Speech (TTS) using Bhashini"""
    config = API_CONFIG[lang]

    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "tts",
                "config": {
                    "language": {"sourceLanguage": config["CODE"]},
                    "serviceId": config["TTS_SERVICE"],
                    "gender": gender,
                    "samplingRate": 8000
                }
            }
        ],
        "inputData": {"input": [{"source": text}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()

    if resp.status_code == 200 and "pipelineResponse" in result:
        audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
        output_filename = os.path.join(
            UPLOAD_FOLDER, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )
        with open(output_filename, "wb") as f:
            f.write(base64.b64decode(audio_content))
        return output_filename
    raise HTTPException(status_code=500, detail=f"TTS failed: {result}")


# ---------------------------
# API Routes
# ---------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Speech Translation API is running"}


@app.get("/languages")
async def get_languages():
    """List all supported languages"""
    languages = [{"code": k, "name": v["NAME"]} for k, v in API_CONFIG.items()]
    return {"languages": languages}


@app.post("/translate-speech")
async def translate_speech(
    audio: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("hi"),
    gender: str = Form("female")
):
    """Main endpoint: Speech → Text → Translate → Speech"""
    if source_lang not in API_CONFIG or target_lang not in API_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid language selection")

    filename = secure_filename(audio.filename)
    audio_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(audio_path, "wb") as f:
        content = await audio.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        f.write(content)

    try:
        recognized_text = asr(audio_path, source_lang)
        translated_text = mt(recognized_text, source_lang, target_lang)
        output_audio_path = tts(translated_text, target_lang, gender)

        os.remove(audio_path)

        return JSONResponse({
            "success": True,
            "original_text": recognized_text,
            "translated_text": translated_text,
            "audio_file": os.path.basename(output_audio_path)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio file"""
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")