# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import os
# import base64  # MISSING IMPORT
# import requests
# from datetime import datetime
# from groq import Groq

# app = Flask(__name__)
# CORS(app)  # Enable CORS for React frontend

# UPLOAD_FOLDER = "uploads"
# OUTPUT_FOLDER = "outputs"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # ---------------------------
# # Config: Language-specific APIs
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

# # Groq API Configuration
# GROQ_API_KEY = "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"

# # ---------------------------
# # Conversation History
# # ---------------------------
# conversation_history = []

# # ---------------------------
# # Helper Functions
# # ---------------------------

# def asr(audio_file_path, lang):
#     """Call Bhashini ASR API for selected language"""
#     config = API_CONFIG[lang]
    
#     # Read and encode audio file to base64
#     with open(audio_file_path, "rb") as audio_file:
#         audio_content = base64.b64encode(audio_file.read()).decode('utf-8')
    
#     # Prepare Bhashini ASR request
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
    
#     # Get language codes
#     source_code = API_CONFIG[source_lang]["CODE"]
#     target_code = API_CONFIG[target_lang]["CODE"]
    
#     # Prepare Bhashini API request
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


# def tts(text, lang, gender="female", speed=1.0):
#     """Generate TTS audio using Bhashini API"""
#     config = API_CONFIG[lang]
    
#     # Prepare Bhashini TTS request
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
#             # Bhashini returns base64 encoded audio
#             audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
            
#             # Save audio to outputs folder
#             output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
#             output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
#             with open(output_path, "wb") as audio_file:
#                 audio_file.write(base64.b64decode(audio_content))
            
#             return output_filename
#         else:
#             raise Exception(f"Bhashini TTS failed: {result}")
#     except Exception as e:
#         raise Exception(f"TTS error: {str(e)}")


# def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None, state="Karnataka"):
#     """Get intelligent answer using Groq API with conversation history"""
#     global conversation_history
    
#     if not GROQ_API_KEY:
#         raise Exception("GROQ_API_KEY not set.")
    
#     try:
#         client = Groq(api_key=GROQ_API_KEY)
        
#         # Build messages with history
#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a helpful agricultural advisor for farmers in India. "
#                     "Provide practical, accurate advice in simple language. "
#                     "Keep responses concise (2–4 sentences). "
#                     "Focus on Indian farming practices, crops, weather conditions, "
#                     "government schemes (PM-KISAN, PMFBY), and local solutions. "
#                     "Remember previous questions in the conversation and refer to them when relevant."
#                 )
#             }
#         ]
        
#         # Add conversation history
#         messages.extend(conversation_history)
        
#         # Add current query
#         messages.append({"role": "user", "content": query_text})
        
#         chat_completion = client.chat.completions.create(
#             messages=messages,
#             model="llama-3.3-70b-versatile",
#             temperature=0.7,
#             max_tokens=300,
#             top_p=1,
#         )
        
#         ai_response = chat_completion.choices[0].message.content
        
#         # Update conversation history
#         conversation_history.append({"role": "user", "content": query_text})
#         conversation_history.append({"role": "assistant", "content": ai_response})
        
#         # Keep only last 10 exchanges (20 messages) to avoid token limits
#         if len(conversation_history) > 20:
#             conversation_history = conversation_history[-20:]
        
#         return ai_response
        
#     except Exception as e:
#         raise Exception(f"Groq API error: {str(e)}")


# def handle_farmer_query(audio_file_path, farmer_lang="te", gender="male", speed=1.0, lat=None, lon=None):
#     """Main pipeline to process farmer query"""
#     # Step 1: ASR
#     print(f"\n🎧 Processing audio in {API_CONFIG[farmer_lang]['NAME']}...")
#     recognized_text = asr(audio_file_path, farmer_lang)
#     print(f"✓ Recognized: {recognized_text}")

#     # Step 2: Translate to English for AI processing
#     print("\n🔄 Translating to English for AI...")
#     text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
#     print(f"✓ Translated: {text_for_ai}")

#     # Step 3: Get AI answer with conversation context (in English)
#     print("\n🤖 Getting AI response with conversation history...")
#     ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
#     print(f"✓ AI Response: {ai_answer_en}")

#     # Step 4: Translate back to farmer's language
#     print(f"\n🔄 Translating back to {API_CONFIG[farmer_lang]['NAME']}...")
#     answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    
#     # Step 5: Generate TTS
#     print("\n🔊 Generating audio response...")
#     tts_filename = tts(answer_local, farmer_lang, gender, speed)
#     print(f"✓ Audio saved: {tts_filename}")

#     return {
#         "success": True,
#         "query_text": recognized_text,
#         "answer_text": answer_local,
#         "audio_url": tts_filename  # Just the filename
#     }


# def clear_conversation_history():
#     """Clear the conversation history"""
#     global conversation_history
#     conversation_history = []
#     print("\n🔄 Conversation history cleared!")


# # ---------------------------
# # Routes
# # ---------------------------

# @app.route("/handle_farmer_query", methods=["POST"])
# def handle_query():
#     if "file" not in request.files:
#         return jsonify({"success": False, "reply": "No file uploaded"}), 400

#     audio_file = request.files["file"]
#     file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
#     audio_file.save(file_path)

#     # Optional: accept query params from frontend
#     farmer_lang = request.form.get("lang", "te")
#     gender = request.form.get("gender", "male")
#     speed = float(request.form.get("speed", 1.0))
#     lat = request.form.get("lat")
#     lon = request.form.get("lon")

#     # Call your pipeline
#     try:
#         result = handle_farmer_query(
#             audio_file_path=file_path,
#             farmer_lang=farmer_lang,
#             gender=gender,
#             speed=speed,
#             lat=lat,
#             lon=lon
#         )
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"success": False, "reply": str(e)}), 500

#     return jsonify(result)


# @app.route("/audio/<filename>", methods=["GET"])
# def serve_audio(filename):
#     """Serve generated audio files"""
#     try:
#         file_path = os.path.join(OUTPUT_FOLDER, filename)
#         if os.path.exists(file_path):
#             return send_file(file_path, mimetype="audio/wav")
#         else:
#             return jsonify({"error": "File not found"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route("/clear_history", methods=["POST"])
# def clear_history():
#     """Clear conversation history"""
#     clear_conversation_history()
#     return jsonify({"success": True, "message": "Conversation history cleared"})


# # if __name__ == "__main__":
# #     app.run(port=5000, debug=True)


from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import requests
from datetime import datetime
from groq import Groq
from typing import Optional

app = FastAPI()

# Enable CORS for React frontend
origins = ["*"]  # Adjust to your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------
# Config: Language-specific APIs
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

# Bhashini Configuration
BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# Groq API Configuration
GROQ_API_KEY = "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"

# ---------------------------
# Conversation History
# ---------------------------
conversation_history = []

# ---------------------------
# Helper Functions
# ---------------------------

def asr(audio_file_path, lang):
    config = API_CONFIG[lang]
    with open(audio_file_path, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode('utf-8')

    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": config["CODE"]}, 
                                                         "serviceId": config["ASR_SERVICE"],
                                                         "audioFormat": "wav",
                                                         "samplingRate": 16000}}],
        "inputData": {"audio": [{"audioContent": audio_content}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["source"]
    else:
        raise Exception(f"Bhashini ASR failed: {result}")


def mt(text, source_lang, target_lang):
    if source_lang == target_lang:
        return text
    source_code = API_CONFIG[source_lang]["CODE"]
    target_code = API_CONFIG[target_lang]["CODE"]

    headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
    payload = {
        "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_code, "targetLanguage": target_code},
                                                                "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                                                                "numTranslation": "True"}}],
        "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        return result["pipelineResponse"][0]["output"][0]["target"]
    else:
        raise Exception(f"Bhashini MT failed: {result}")


def tts(text, lang, gender="female", speed=1.0):
    config = API_CONFIG[lang]
    headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
    payload = {
        "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": config["CODE"]},
                                                         "serviceId": config["TTS_SERVICE"],
                                                         "gender": gender,
                                                         "samplingRate": 8000}}],
        "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
    }

    resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
    result = resp.json()
    if resp.status_code == 200 and "pipelineResponse" in result:
        audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
        output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(output_path, "wb") as audio_file:
            audio_file.write(base64.b64decode(audio_content))
        return output_filename
    else:
        raise Exception(f"Bhashini TTS failed: {result}")


def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None):
    global conversation_history
    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": (
        "You are a helpful agricultural advisor for farmers in India. "
        "Provide practical, accurate advice in simple language. "
        "Keep responses concise (2–4 sentences). "
        "Focus on Indian farming practices, crops, weather conditions, "
        "government schemes (PM-KISAN, PMFBY), and local solutions. "
        "Remember previous questions in the conversation and refer to them when relevant."
    )}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": query_text})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=300,
        top_p=1,
    )
    ai_response = chat_completion.choices[0].message.content

    conversation_history.append({"role": "user", "content": query_text})
    conversation_history.append({"role": "assistant", "content": ai_response})
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    return ai_response


def handle_farmer_query(audio_file_path, farmer_lang="te", gender="male", speed=1.0, lat=None, lon=None):
    recognized_text = asr(audio_file_path, farmer_lang)
    text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
    ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
    answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    tts_filename = tts(answer_local, farmer_lang, gender, speed)

    return {
        "success": True,
        "query_text": recognized_text,
        "answer_text": answer_local,
        "audio_url": tts_filename
    }


def clear_conversation_history():
    global conversation_history
    conversation_history = []

# ---------------------------
# Routes
# ---------------------------

@app.post("/handle_farmer_query")
async def handle_query(
    file: UploadFile = File(...),
    lang: str = Form("te"),
    gender: str = Form("male"),
    speed: float = Form(1.0),
    lat: Optional[str] = Form(None),
    lon: Optional[str] = Form(None)
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        result = handle_farmer_query(file_path, farmer_lang=lang, gender=gender, speed=speed, lat=lat, lon=lon)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
def serve_audio(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.post("/clear_history")
def clear_history():
    clear_conversation_history()
    return JSONResponse({"success": True, "message": "Conversation history cleared"})