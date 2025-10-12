# # from flask import Flask, request, jsonify, send_file
# # from flask_cors import CORS
# # import os
# # import base64  # MISSING IMPORT
# # import requests
# # from datetime import datetime
# # from groq import Groq

# # app = Flask(__name__)
# # CORS(app)  # Enable CORS for React frontend

# # UPLOAD_FOLDER = "uploads"
# # OUTPUT_FOLDER = "outputs"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # # ---------------------------
# # # Config: Language-specific APIs
# # # ---------------------------

# # API_CONFIG = {
# #     "en": {
# #         "NAME": "English",
# #         "CODE": "en",
# #         "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4",
# #         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"
# #     },
# #     "te": {
# #         "NAME": "Telugu (తెలుగు)",
# #         "CODE": "te",
# #         "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4",
# #         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"
# #     },
# #     "hi": {
# #         "NAME": "Hindi (हिंदी)",
# #         "CODE": "hi",
# #         "ASR_SERVICE": "ai4bharat/conformer-hi-gpu--t4",
# #         "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
# #     },
# # }

# # # Bhashini Configuration
# # BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
# # BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# # # Groq API Configuration
# # GROQ_API_KEY = "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"

# # # ---------------------------
# # # Conversation History
# # # ---------------------------
# # conversation_history = []

# # # ---------------------------
# # # Helper Functions
# # # ---------------------------

# # def asr(audio_file_path, lang):
# #     """Call Bhashini ASR API for selected language"""
# #     config = API_CONFIG[lang]
    
# #     # Read and encode audio file to base64
# #     with open(audio_file_path, "rb") as audio_file:
# #         audio_content = base64.b64encode(audio_file.read()).decode('utf-8')
    
# #     # Prepare Bhashini ASR request
# #     headers = {
# #         "Authorization": BHASHINI_AUTH_KEY,
# #         "Content-Type": "application/json"
# #     }
    
# #     payload = {
# #         "pipelineTasks": [
# #             {
# #                 "taskType": "asr",
# #                 "config": {
# #                     "language": {
# #                         "sourceLanguage": config["CODE"]
# #                     },
# #                     "serviceId": config["ASR_SERVICE"],
# #                     "audioFormat": "wav",
# #                     "samplingRate": 16000
# #                 }
# #             }
# #         ],
# #         "inputData": {
# #             "audio": [
# #                 {
# #                     "audioContent": audio_content
# #                 }
# #             ]
# #         }
# #     }
    
# #     try:
# #         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
# #         result = resp.json()
        
# #         if resp.status_code == 200 and "pipelineResponse" in result:
# #             recognized_text = result["pipelineResponse"][0]["output"][0]["source"]
# #             return recognized_text
# #         else:
# #             raise Exception(f"Bhashini ASR failed: {result}")
# #     except Exception as e:
# #         raise Exception(f"ASR error: {str(e)}")


# # def mt(text, source_lang, target_lang):
# #     """Translate text using Bhashini API"""
# #     if source_lang == target_lang:
# #         return text
    
# #     # Get language codes
# #     source_code = API_CONFIG[source_lang]["CODE"]
# #     target_code = API_CONFIG[target_lang]["CODE"]
    
# #     # Prepare Bhashini API request
# #     headers = {
# #         "Authorization": BHASHINI_AUTH_KEY,
# #         "Content-Type": "application/json"
# #     }
    
# #     payload = {
# #         "pipelineTasks": [
# #             {
# #                 "taskType": "translation",
# #                 "config": {
# #                     "language": {
# #                         "sourceLanguage": source_code,
# #                         "targetLanguage": target_code
# #                     },
# #                     "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
# #                     "numTranslation": "True"
# #                 }
# #             }
# #         ],
# #         "inputData": {
# #             "input": [
# #                 {
# #                     "source": text
# #                 }
# #             ],
# #             "audio": [
# #                 {
# #                     "audioContent": None
# #                 }
# #             ]
# #         }
# #     }
    
# #     try:
# #         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
# #         result = resp.json()
        
# #         if resp.status_code == 200 and "pipelineResponse" in result:
# #             translation_output = result["pipelineResponse"][0]["output"][0]["target"]
# #             return translation_output
# #         else:
# #             raise Exception(f"Bhashini MT failed: {result}")
# #     except Exception as e:
# #         raise Exception(f"Translation error: {str(e)}")


# # def tts(text, lang, gender="female", speed=1.0):
# #     """Generate TTS audio using Bhashini API"""
# #     config = API_CONFIG[lang]
    
# #     # Prepare Bhashini TTS request
# #     headers = {
# #         "Authorization": BHASHINI_AUTH_KEY,
# #         "Content-Type": "application/json"
# #     }
    
# #     payload = {
# #         "pipelineTasks": [
# #             {
# #                 "taskType": "tts",
# #                 "config": {
# #                     "language": {
# #                         "sourceLanguage": config["CODE"]
# #                     },
# #                     "serviceId": config["TTS_SERVICE"],
# #                     "gender": gender,
# #                     "samplingRate": 8000
# #                 }
# #             }
# #         ],
# #         "inputData": {
# #             "input": [
# #                 {
# #                     "source": text
# #                 }
# #             ],
# #             "audio": [
# #                 {
# #                     "audioContent": None
# #                 }
# #             ]
# #         }
# #     }
    
# #     try:
# #         resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
# #         result = resp.json()
        
# #         if resp.status_code == 200 and "pipelineResponse" in result:
# #             # Bhashini returns base64 encoded audio
# #             audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
            
# #             # Save audio to outputs folder
# #             output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
# #             output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
# #             with open(output_path, "wb") as audio_file:
# #                 audio_file.write(base64.b64decode(audio_content))
            
# #             return output_filename
# #         else:
# #             raise Exception(f"Bhashini TTS failed: {result}")
# #     except Exception as e:
# #         raise Exception(f"TTS error: {str(e)}")


# # def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None, state="Karnataka"):
# #     """Get intelligent answer using Groq API with conversation history"""
# #     global conversation_history
    
# #     if not GROQ_API_KEY:
# #         raise Exception("GROQ_API_KEY not set.")
    
# #     try:
# #         client = Groq(api_key=GROQ_API_KEY)
        
# #         # Build messages with history
# #         messages = [
# #             {
# #                 "role": "system",
# #                 "content": (
# #                     "You are a helpful agricultural advisor for farmers in India. "
# #                     "Provide practical, accurate advice in simple language. "
# #                     "Keep responses concise (2–4 sentences). "
# #                     "Focus on Indian farming practices, crops, weather conditions, "
# #                     "government schemes (PM-KISAN, PMFBY), and local solutions. "
# #                     "Remember previous questions in the conversation and refer to them when relevant."
# #                 )
# #             }
# #         ]
        
# #         # Add conversation history
# #         messages.extend(conversation_history)
        
# #         # Add current query
# #         messages.append({"role": "user", "content": query_text})
        
# #         chat_completion = client.chat.completions.create(
# #             messages=messages,
# #             model="llama-3.3-70b-versatile",
# #             temperature=0.7,
# #             max_tokens=300,
# #             top_p=1,
# #         )
        
# #         ai_response = chat_completion.choices[0].message.content
        
# #         # Update conversation history
# #         conversation_history.append({"role": "user", "content": query_text})
# #         conversation_history.append({"role": "assistant", "content": ai_response})
        
# #         # Keep only last 10 exchanges (20 messages) to avoid token limits
# #         if len(conversation_history) > 20:
# #             conversation_history = conversation_history[-20:]
        
# #         return ai_response
        
# #     except Exception as e:
# #         raise Exception(f"Groq API error: {str(e)}")


# # def handle_farmer_query(audio_file_path, farmer_lang="te", gender="male", speed=1.0, lat=None, lon=None):
# #     """Main pipeline to process farmer query"""
# #     # Step 1: ASR
# #     print(f"\n🎧 Processing audio in {API_CONFIG[farmer_lang]['NAME']}...")
# #     recognized_text = asr(audio_file_path, farmer_lang)
# #     print(f"✓ Recognized: {recognized_text}")

# #     # Step 2: Translate to English for AI processing
# #     print("\n🔄 Translating to English for AI...")
# #     text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
# #     print(f"✓ Translated: {text_for_ai}")

# #     # Step 3: Get AI answer with conversation context (in English)
# #     print("\n🤖 Getting AI response with conversation history...")
# #     ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
# #     print(f"✓ AI Response: {ai_answer_en}")

# #     # Step 4: Translate back to farmer's language
# #     print(f"\n🔄 Translating back to {API_CONFIG[farmer_lang]['NAME']}...")
# #     answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    
# #     # Step 5: Generate TTS
# #     print("\n🔊 Generating audio response...")
# #     tts_filename = tts(answer_local, farmer_lang, gender, speed)
# #     print(f"✓ Audio saved: {tts_filename}")

# #     return {
# #         "success": True,
# #         "query_text": recognized_text,
# #         "answer_text": answer_local,
# #         "audio_url": tts_filename  # Just the filename
# #     }


# # def clear_conversation_history():
# #     """Clear the conversation history"""
# #     global conversation_history
# #     conversation_history = []
# #     print("\n🔄 Conversation history cleared!")


# # # ---------------------------
# # # Routes
# # # ---------------------------

# # @app.route("/handle_farmer_query", methods=["POST"])
# # def handle_query():
# #     if "file" not in request.files:
# #         return jsonify({"success": False, "reply": "No file uploaded"}), 400

# #     audio_file = request.files["file"]
# #     file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
# #     audio_file.save(file_path)

# #     # Optional: accept query params from frontend
# #     farmer_lang = request.form.get("lang", "te")
# #     gender = request.form.get("gender", "male")
# #     speed = float(request.form.get("speed", 1.0))
# #     lat = request.form.get("lat")
# #     lon = request.form.get("lon")

# #     # Call your pipeline
# #     try:
# #         result = handle_farmer_query(
# #             audio_file_path=file_path,
# #             farmer_lang=farmer_lang,
# #             gender=gender,
# #             speed=speed,
# #             lat=lat,
# #             lon=lon
# #         )
# #     except Exception as e:
# #         print(f"Error: {str(e)}")
# #         return jsonify({"success": False, "reply": str(e)}), 500

# #     return jsonify(result)


# # @app.route("/audio/<filename>", methods=["GET"])
# # def serve_audio(filename):
# #     """Serve generated audio files"""
# #     try:
# #         file_path = os.path.join(OUTPUT_FOLDER, filename)
# #         if os.path.exists(file_path):
# #             return send_file(file_path, mimetype="audio/wav")
# #         else:
# #             return jsonify({"error": "File not found"}), 404
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500


# # @app.route("/clear_history", methods=["POST"])
# # def clear_history():
# #     """Clear conversation history"""
# #     clear_conversation_history()
# #     return jsonify({"success": True, "message": "Conversation history cleared"})


# # # if __name__ == "__main__":
# # #     app.run(port=5000, debug=True)


# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import base64
# import requests
# from datetime import datetime
# from groq import Groq
# from typing import Optional

# app = FastAPI()

# # Enable CORS for React frontend
# origins = ["*"]  # Adjust to your frontend domain in production
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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
#     config = API_CONFIG[lang]
#     with open(audio_file_path, "rb") as audio_file:
#         audio_content = base64.b64encode(audio_file.read()).decode('utf-8')

#     headers = {
#         "Authorization": BHASHINI_AUTH_KEY,
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": config["CODE"]}, 
#                                                          "serviceId": config["ASR_SERVICE"],
#                                                          "audioFormat": "wav",
#                                                          "samplingRate": 16000}}],
#         "inputData": {"audio": [{"audioContent": audio_content}]}
#     }

#     resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#     result = resp.json()
#     if resp.status_code == 200 and "pipelineResponse" in result:
#         return result["pipelineResponse"][0]["output"][0]["source"]
#     else:
#         raise Exception(f"Bhashini ASR failed: {result}")


# def mt(text, source_lang, target_lang):
#     if source_lang == target_lang:
#         return text
#     source_code = API_CONFIG[source_lang]["CODE"]
#     target_code = API_CONFIG[target_lang]["CODE"]

#     headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
#     payload = {
#         "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_code, "targetLanguage": target_code},
#                                                                 "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
#                                                                 "numTranslation": "True"}}],
#         "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
#     }

#     resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#     result = resp.json()
#     if resp.status_code == 200 and "pipelineResponse" in result:
#         return result["pipelineResponse"][0]["output"][0]["target"]
#     else:
#         raise Exception(f"Bhashini MT failed: {result}")


# def tts(text, lang, gender="female", speed=1.0):
#     config = API_CONFIG[lang]
#     headers = {"Authorization": BHASHINI_AUTH_KEY, "Content-Type": "application/json"}
#     payload = {
#         "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": config["CODE"]},
#                                                          "serviceId": config["TTS_SERVICE"],
#                                                          "gender": gender,
#                                                          "samplingRate": 8000}}],
#         "inputData": {"input": [{"source": text}], "audio": [{"audioContent": None}]}
#     }

#     resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
#     result = resp.json()
#     if resp.status_code == 200 and "pipelineResponse" in result:
#         audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
#         output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
#         output_path = os.path.join(OUTPUT_FOLDER, output_filename)
#         with open(output_path, "wb") as audio_file:
#             audio_file.write(base64.b64decode(audio_content))
#         return output_filename
#     else:
#         raise Exception(f"Bhashini TTS failed: {result}")


# def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None):
#     global conversation_history
#     client = Groq(api_key=GROQ_API_KEY)
#     messages = [{"role": "system", "content": (
#         "You are a helpful agricultural advisor for farmers in India. "
#         "Provide practical, accurate advice in simple language. "
#         "Keep responses concise (2–4 sentences). "
#         "Focus on Indian farming practices, crops, weather conditions, "
#         "government schemes (PM-KISAN, PMFBY), and local solutions. "
#         "Remember previous questions in the conversation and refer to them when relevant."
#     )}]
#     messages.extend(conversation_history)
#     messages.append({"role": "user", "content": query_text})

#     chat_completion = client.chat.completions.create(
#         messages=messages,
#         model="llama-3.3-70b-versatile",
#         temperature=0.7,
#         max_tokens=300,
#         top_p=1,
#     )
#     ai_response = chat_completion.choices[0].message.content

#     conversation_history.append({"role": "user", "content": query_text})
#     conversation_history.append({"role": "assistant", "content": ai_response})
#     if len(conversation_history) > 20:
#         conversation_history = conversation_history[-20:]
#     return ai_response


# def handle_farmer_query(audio_file_path, farmer_lang="te", gender="male", speed=1.0, lat=None, lon=None):
#     recognized_text = asr(audio_file_path, farmer_lang)
#     text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
#     ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
#     answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
#     tts_filename = tts(answer_local, farmer_lang, gender, speed)

#     return {
#         "success": True,
#         "query_text": recognized_text,
#         "answer_text": answer_local,
#         "audio_url": tts_filename
#     }


# def clear_conversation_history():
#     global conversation_history
#     conversation_history = []

# # ---------------------------
# # Routes
# # ---------------------------

# @app.post("/handle_farmer_query")
# async def handle_query(
#     file: UploadFile = File(...),
#     lang: str = Form("te"),
#     gender: str = Form("male"),
#     speed: float = Form(1.0),
#     lat: Optional[str] = Form(None),
#     lon: Optional[str] = Form(None)
# ):
#     try:
#         file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         result = handle_farmer_query(file_path, farmer_lang=lang, gender=gender, speed=speed, lat=lat, lon=lon)
#         return JSONResponse(result)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/audio/{filename}")
# def serve_audio(filename: str):
#     file_path = os.path.join(OUTPUT_FOLDER, filename)
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="audio/wav")
#     else:
#         raise HTTPException(status_code=404, detail="File not found")


# @app.post("/clear_history")
# def clear_history():
#     clear_conversation_history()
#     return JSONResponse({"success": True, "message": "Conversation history cleared"})


from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import requests
from datetime import datetime, timedelta # Added timedelta for date calculation
from groq import Groq
import re
import shutil

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------
# Config: Language-specific settings (22 Languages)
# ---------------------------

# Bhashini Configuration
BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
# NOTE: Replace with your actual key if needed, but keeping the placeholder key here
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# Groq API Configuration
GROQ_API_KEY = "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"

# Config: Comprehensive Language-specific settings
# ASR/TTS Services are chosen based on the most robust multilingual models available.
API_CONFIG = {
    # English (Specific ASR, Misc TTS)
    "en": {"NAME": "English", "CODE": "en", "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"},

    # Indo-Aryan Group (Multilingual ASR & TTS)
    "hi": {"NAME": "Hindi (हिंदी)", "CODE": "hi", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "bn": {"NAME": "Bengali (বাংলা)", "CODE": "bn", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "mr": {"NAME": "Marathi (मराठी)", "CODE": "mr", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "gu": {"NAME": "Gujarati (ગુજરાતી)", "CODE": "gu", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "or": {"NAME": "Odia (ଓଡ଼ିଆ)", "CODE": "or", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "pa": {"NAME": "Punjabi (ਪੰਜਾਬੀ)", "CODE": "pa", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "as": {"NAME": "Assamese (অসমীয়া)", "CODE": "as", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"}, 
    
    # Dravidian Group (Multilingual ASR & TTS)
    "te": {"NAME": "Telugu (తెలుగు)", "CODE": "te", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "kn": {"NAME": "Kannada (ಕನ್ನಡ)", "CODE": "kn", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "ta": {"NAME": "Tamil (தமிழ்)", "CODE": "ta", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "ml": {"NAME": "Malayalam (മലയാളം)", "CODE": "ml", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    
    # Other Scheduled Languages (Using general Bhashini multilingual ASR and IITM/Misc TTS)
    "ur": {"NAME": "Urdu (اُردُو)", "CODE": "ur", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sa": {"NAME": "Sanskrit (संस्कृतम्)", "CODE": "sa", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "brx": {"NAME": "Bodo (बर')", "CODE": "brx", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"},
    "doi": {"NAME": "Dogri (डोगरी)", "CODE": "doi", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "ks": {"NAME": "Kashmiri (کٲشُر)", "CODE": "ks", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "gom": {"NAME": "Goan Konkani (कोंकणी)", "CODE": "gom", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "mai": {"NAME": "Maithili (मैथिली)", "CODE": "mai", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "ne": {"NAME": "Nepali (नेपाली)", "CODE": "ne", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sat": {"NAME": "Santali (ᱥᱟᱱᱛᱟᱲᱤ)", "CODE": "sat", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sd": {"NAME": "Sindhi (سنڌي)", "CODE": "sd", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
}

# ---------------------------
# Conversation History (Global state for chat context)
# ---------------------------
conversation_history = []

# ---------------------------
# Helper Functions
# ---------------------------

def asr(audio_file_path, lang):
    """Call Bhashini ASR API for selected language"""
    config = API_CONFIG[lang]
    
    # Read and encode audio file to base64
    with open(audio_file_path, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode('utf-8')
    
    # Prepare Bhashini ASR request
    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {
                        "sourceLanguage": config["CODE"]
                    },
                    "serviceId": config["ASR_SERVICE"],
                    "audioFormat": "wav",
                    "samplingRate": 16000
                }
            }
        ],
        "inputData": {
            "audio": [
                {
                    "audioContent": audio_content
                }
            ]
        }
    }
    
    try:
        resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        if resp.status_code == 200 and "pipelineResponse" in result:
            recognized_text = result["pipelineResponse"][0]["output"][0]["source"]
            return recognized_text
        else:
            error_detail = result.get("detail", result)
            raise Exception(f"Bhashini ASR failed: {error_detail}")
    except Exception as e:
        raise Exception(f"ASR error: {str(e)}")


def mt(text, source_lang, target_lang):
    """Translate text using Bhashini API"""
    if source_lang == target_lang:
        return text
    
    # Get language codes
    source_code = API_CONFIG[source_lang]["CODE"]
    target_code = API_CONFIG[target_lang]["CODE"]
    
    # Prepare Bhashini API request
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
                        "sourceLanguage": source_code,
                        "targetLanguage": target_code
                    },
                    # Using the general IndicTrans V2 translation service ID, which covers all 22 languages
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4", 
                    "numTranslation": "True"
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": text
                }
            ],
            "audio": [
                {
                    "audioContent": None
                }
            ]
        }
    }
    
    try:
        resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        if resp.status_code == 200 and "pipelineResponse" in result:
            translation_output = result["pipelineResponse"][0]["output"][0]["target"]
            return translation_output
        else:
            error_detail = result.get("detail", result)
            raise Exception(f"Bhashini MT failed: {error_detail}")
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")


def tts(text, lang, gender="female", speed=1.0):
    """Generate TTS audio using Bhashini API"""
    config = API_CONFIG[lang]
    
    # Prepare Bhashini TTS request
    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "pipelineTasks": [
            {
                "taskType": "tts",
                "config": {
                    "language": {
                        "sourceLanguage": config["CODE"]
                    },
                    "serviceId": config["TTS_SERVICE"],
                    "gender": gender,
                    "samplingRate": 8000
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": text
                }
            ],
            "audio": [
                {
                    "audioContent": None
                }
            ]
        }
    }
    
    try:
        resp = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        if resp.status_code == 200 and "pipelineResponse" in result:
            # Bhashini returns base64 encoded audio
            audio_content = result["pipelineResponse"][0]["audio"][0]["audioContent"]
            
            # Save audio to OUTPUT_FOLDER
            output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            with open(output_path, "wb") as audio_file:
                audio_file.write(base64.b64decode(audio_content))
            
            print(f"✓ Audio saved to: {output_path}")
            return output_filename  # Return just filename
        else:
            error_detail = result.get("detail", result)
            raise Exception(f"Bhashini TTS failed: {error_detail}")
    except Exception as e:
        raise Exception(f"TTS error: {str(e)}")


def get_weather_tense(weather_date_str):
    """Determine tense based on weather date"""
    if not weather_date_str:
        return "today"
    today = datetime.now().date()
    try:
        query_date = datetime.strptime(weather_date_str, "%Y-%m-%d").date()
        if query_date < today:
            return "past"
        elif query_date == today:
            return "today"
        else:
            return "future"
    except:
        return "future"


def extract_weather_date(query_text):
    """Ask AI to extract a date from the query. Returns today's date if none found."""
    if not GROQ_API_KEY:
        return None
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        
        prompt = (
            f"Today's date is {today_str}.\n"
            "Extract the date the user wants weather information for from this query.\n"
            "Return ONLY the date in YYYY-MM-DD format, nothing else.\n"
            "Examples:\n"
            "- 'tomorrow' -> calculate tomorrow's date\n"
            "- 'next Monday' -> calculate that date\n"
            "- 'January 15' -> 2025-01-15 (or 2026 if it's past that date this year)\n"
            f"- no date mentioned -> {today_str}\n\n"
            f"Query: {query_text}\n\n"
            "Return only the date in YYYY-MM-DD format:"
        )
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You extract dates from text and return them in YYYY-MM-DD format. Return ONLY the date, no other text."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=50,
        )
        
        extracted = response.choices[0].message.content.strip()
        print(f"AI raw response: '{extracted}'")
        
        # Try to extract YYYY-MM-DD pattern from response
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', extracted)
        if date_match:
            return date_match.group(0)
        
        # Fallback to today if no valid date found
        return today_str
        
    except Exception as e:
        print(f"Error in extract_weather_date: {e}")
        return datetime.now().strftime("%Y-%m-%d")


def get_weather(lat, lon, date=None):
    """Fetch weather for a given date. If date is None, fetch current weather."""
    try:
        if date:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max"
                f"&start_date={date}&end_date={date}&timezone=Asia/Kolkata"
            )
        else:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if date and "daily" in data:
            weather = {
                "temperature_max": data["daily"]["temperature_2m_max"][0],
                "temperature_min": data["daily"]["temperature_2m_min"][0],
                "precipitation": data["daily"]["precipitation_sum"][0],
                "windspeed": data["daily"]["windspeed_10m_max"][0],
                "condition_code": data["daily"]["weathercode"][0]
            }
        elif "current_weather" in data:
            weather = data["current_weather"]
            weather["condition_code"] = weather.get("weathercode", -1)
            # For current weather, use the same keys as daily for consistency
            weather["temperature_max"] = weather.get("temperature")
            weather["temperature_min"] = weather.get("temperature")
            weather["precipitation"] = 0 # Assume 0 for current unless specified
            weather["windspeed"] = weather.get("windspeed")
        else:
            return None

        weather_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        weather["condition"] = weather_map.get(weather.get("condition_code", -1), "Unknown")
        return weather
    except Exception as e:
        print(f"Weather API error: {e}")
        return None


def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None, state="Karnataka"):
    """Get intelligent answer using Groq API with conversation history, prioritizing weather."""
    global conversation_history
    
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not set.")
    
    # Check for weather query (keywords in multiple languages)
    weather_keywords = [
        "weather", "temperature", "rain", "climate", "mausam", "tapman", "barish", "jalvayu", 
        "వాతావరణం", "తాపోగ్రత", "వర్షం", "मौसम", "तापमान", "बारिश", "जलवायु" # Adding some common language terms
    ]
    is_weather_query = any(word.lower() in query_text.lower() for word in weather_keywords)

    # ---------------- WEATHER HANDLING ----------------
    weather_date = extract_weather_date(query_text) if is_weather_query else None

    if is_weather_query and lat is not None and lon is not None and weather_date:
        weather_data = get_weather(lat, lon, weather_date)
        if weather_data:
            weather_tense = get_weather_tense(weather_date)
            
            if weather_tense == "past":
                day_phrase = f"on {weather_date}"
                tense_advice = "The weather was"
            elif weather_tense == "today":
                day_phrase = "today"
                tense_advice = "The weather is expected to be"
            else:
                day_phrase = f"on {weather_date}"
                tense_advice = "The weather is predicted to be"

            weather_prompt = (
                f"Tell a farmer about the weather in simple language for {day_phrase}. "
                f"Location: {state}. {tense_advice}: {weather_data['condition']}. "
                f"Max temp: {weather_data.get('temperature_max', 'N/A')}°C. "
                f"Min temp: {weather_data.get('temperature_min', 'N/A')}°C. "
                f"Precipitation: {weather_data.get('precipitation', 'N/A')}mm. "
                f"Wind speed: {weather_data['windspeed']} km/h. "
                "Give practical farming advice in 2–3 sentences based on these conditions. "
                "Do NOT mention the actual date; instead use the phrase provided above (e.g., 'today', 'on that day'). "
                f"Write the response in the appropriate {weather_tense} tense."
            )
            
            # Use Groq to generate a simple, actionable weather report
            try:
                client = Groq(api_key=GROQ_API_KEY)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful agricultural advisor, prioritizing local weather details."},
                        {"role": "user", "content": weather_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=200,
                    top_p=1,
                )
                return chat_completion.choices[0].message.content
            except:
                return f"Weather on {day_phrase} in {state}: {weather_data.get('temperature_max')}°C, {weather_data['condition']}."
        else:
            return "I couldn't fetch the weather information right now. Please try again."

    # ---------------- GENERAL AI HANDLING ----------------
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build messages with history
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful agricultural advisor for farmers in India. "
                    "Provide practical, accurate advice in simple language. "
                    "Keep responses concise (2–4 sentences). "
                    "Focus on Indian farming practices, crops, government schemes (PM-KISAN, PMFBY), and local solutions. "
                    "Remember previous questions in the conversation and refer to them when relevant."
                )
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current query
        messages.append({"role": "user", "content": query_text})
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300,
            top_p=1,
        )
        
        ai_response = chat_completion.choices[0].message.content
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": query_text})
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Keep only last 10 exchanges (20 messages) to avoid token limits
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return ai_response
        
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")


def handle_farmer_query(audio_file_path, farmer_lang="te", gender="male", speed=1.0, lat=None, lon=None, state=None):
    """Main pipeline to process farmer query"""
    # Step 1: ASR
    print(f"\n🎧 Processing audio in {API_CONFIG[farmer_lang]['NAME']}...")
    recognized_text = asr(audio_file_path, farmer_lang)
    print(f"✓ Recognized: {recognized_text}")

    # Step 2: Translate to English for AI processing
    print("\n🔄 Translating to English for AI...")
    text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
    print(f"✓ Translated: {text_for_ai}")

    # Step 3: Get AI answer with conversation context (in English)
    print("\n🤖 Getting AI response with conversation history...")
    ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon, state)
    print(f"✓ AI Response: {ai_answer_en}")

    # Step 4: Translate back to farmer's language
    print(f"\n🔄 Translating back to {API_CONFIG[farmer_lang]['NAME']}...")
    answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    print(f"✓ Translated Answer: {answer_local}")
    
    # Step 5: Generate TTS
    print("\n🔊 Generating audio response...")
    tts_filename = tts(answer_local, farmer_lang, gender, speed)
    print(f"✓ Audio saved: {tts_filename}")

    # The frontend expects 'audio_file' to contain the path outputs/filename.wav
    return {
        "success": True,
        "query_text": recognized_text,
        "answer_text": answer_local,
        "audio_file": f"outputs/{tts_filename}"
    }


def clear_conversation_history():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    print("\n🔄 Conversation history cleared!")


# ---------------------------
# FastAPI Routes
# ---------------------------

@app.post("/handle_farmer_query")
async def handle_query(
    file: UploadFile,
    lang: str = Form("te"),
    gender: str = Form("male"),
    speed: float = Form(1.0),
    lat: str = Form(None),
    lon: str = Form(None),
    state: str = Form(None)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        with open(file_path, "wb") as f:
            # Use file.file.read() for FastAPI UploadFile
            content = await file.read()
            f.write(content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "reply": f"File save error: {str(e)}"})

    # Call the main pipeline
    try:
        result = handle_farmer_query(
            audio_file_path=file_path,
            farmer_lang=lang,
            gender=gender,
            speed=speed,
            lat=lat,
            lon=lon,
            state=state
        )
    except Exception as e:
        # Ensure file cleanup even on pipeline failure
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(status_code=500, content={"success": False, "reply": str(e)})

    # Cleanup uploaded file after successful processing
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return JSONResponse(content=result)


@app.post("/clear_history")
async def api_clear_history():
    """Endpoint to clear conversation history."""
    clear_conversation_history()
    return JSONResponse(content={"success": True, "message": "Conversation history cleared"})


@app.get("/outputs/{filename}")
async def serve_output_audio(filename: str):
    """Serve generated audio files from outputs folder"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        # FileResponse is the FastAPI equivalent of Flask's send_file
        return FileResponse(file_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="File not found")


# if __name__ == "__main__":
#     import uvicorn
#     # Use reload=True for development (like Flask debug=True)
#     uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)