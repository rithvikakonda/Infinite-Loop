# from fastapi import FastAPI, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import base64
# import requests
# from datetime import datetime
# from groq import Groq
# import re
# import shutil

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # adjust for production
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

# import requests
# import os
# from datetime import datetime
# from groq import Groq
# import re
# import base64

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

# # Groq API Configuration
# GROQ_API_KEY = "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"

# # ---------------------------
# # Helper Functions
# # ---------------------------

# def select_language():
#     """Interactive language selection"""
#     print("\n" + "="*60)
#     print("🌍 SELECT YOUR LANGUAGE / अपनी भाषा चुनें / మీ భాషను ఎంచుకోండి")
#     print("="*60)
#     print("1. English")
#     print("2. తెలుగు (Telugu)")
#     print("3. हिंदी (Hindi)")
#     print("="*60)
    
#     while True:
#         choice = input("\nEnter your choice (1/2/3): ").strip()
#         if choice == "1":
#             return "en"
#         elif choice == "2":
#             return "te"
#         elif choice == "3":
#             return "hi"
#         else:
#             print("❌ Invalid choice! Please enter 1, 2, or 3.")


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
            
#             # Save audio to OUTPUT_FOLDER (not root directory)
#             output_filename = f"output_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
#             output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
#             with open(output_path, "wb") as audio_file:
#                 audio_file.write(base64.b64decode(audio_content))
            
#             print(f"✓ Audio saved to: {output_path}")
#             return output_filename  # Return just filename
#         else:
#             raise Exception(f"Bhashini TTS failed: {result}")
#     except Exception as e:
#         raise Exception(f"TTS error: {str(e)}")


# def get_weather_tense(weather_date_str):
#     """Determine tense based on weather date"""
#     if not weather_date_str:
#         return "today"
#     today = datetime.now().date()
#     try:
#         query_date = datetime.strptime(weather_date_str, "%Y-%m-%d").date()
#         if query_date < today:
#             return "past"
#         elif query_date == today:
#             return "today"
#         else:
#             return "future"
#     except:
#         return "future"


# def extract_weather_date(query_text):
#     """Ask AI to extract a date from the query. Returns today's date if none found."""
#     if not GROQ_API_KEY:
#         return None
    
#     try:
#         client = Groq(api_key=GROQ_API_KEY)
#         today = datetime.now()
#         today_str = today.strftime("%Y-%m-%d")
        
#         prompt = (
#             f"Today's date is {today_str}.\n"
#             "Extract the date the user wants weather information for from this query.\n"
#             "Return ONLY the date in YYYY-MM-DD format, nothing else.\n"
#             "Examples:\n"
#             "- 'tomorrow' -> calculate tomorrow's date\n"
#             "- 'next Monday' -> calculate that date\n"
#             "- 'January 15' -> 2025-01-15 (or 2026 if it's past that date this year)\n"
#             f"- no date mentioned -> {today_str}\n\n"
#             f"Query: {query_text}\n\n"
#             "Return only the date in YYYY-MM-DD format:"
#         )
        
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": "You extract dates from text and return them in YYYY-MM-DD format. Return ONLY the date, no other text."},
#                 {"role": "user", "content": prompt}
#             ],
#             model="llama-3.3-70b-versatile",
#             temperature=0,
#             max_tokens=50,
#         )
        
#         extracted = response.choices[0].message.content.strip()
#         print(f"AI raw response: '{extracted}'")
        
#         # Try to extract YYYY-MM-DD pattern from response
#         date_match = re.search(r'\d{4}-\d{2}-\d{2}', extracted)
#         if date_match:
#             return date_match.group(0)
        
#         # Fallback to today if no valid date found
#         return today_str
        
#     except Exception as e:
#         print(f"Error in extract_weather_date: {e}")
#         return datetime.now().strftime("%Y-%m-%d")


# def get_weather(lat, lon, date=None):
#     """Fetch weather for a given date. If date is None, fetch current weather."""
#     try:
#         if date:
#             url = (
#                 f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
#                 f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max"
#                 f"&start_date={date}&end_date={date}&timezone=Asia/Kolkata"
#             )
#         else:
#             url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        
#         resp = requests.get(url, timeout=10)
#         data = resp.json()

#         if date and "daily" in data:
#             weather = {
#                 "temperature_max": data["daily"]["temperature_2m_max"][0],
#                 "temperature_min": data["daily"]["temperature_2m_min"][0],
#                 "precipitation": data["daily"]["precipitation_sum"][0],
#                 "windspeed": data["daily"]["windspeed_10m_max"][0],
#                 "condition_code": data["daily"]["weathercode"][0]
#             }
#         elif "current_weather" in data:
#             weather = data["current_weather"]
#             weather["condition_code"] = weather.get("weathercode", -1)
#         else:
#             return None

#         weather_map = {
#             0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
#             45: "Fog", 48: "Depositing rime fog",
#             51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
#             56: "Light freezing drizzle", 57: "Dense freezing drizzle",
#             61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
#             66: "Light freezing rain", 67: "Heavy freezing rain",
#             71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
#             80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
#             85: "Slight snow showers", 86: "Heavy snow showers",
#             95: "Thunderstorm", 96: "Thunderstorm with slight hail",
#             99: "Thunderstorm with heavy hail"
#         }
#         weather["condition"] = weather_map.get(weather.get("condition_code", -1), "Unknown")
#         return weather
#     except:
#         return None


# def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None, state="Karnataka"):
#     """Get intelligent answer using Groq API or fetch weather based on query"""
#     # Check for weather query (keywords in multiple languages)
#     weather_keywords = [
#         "weather", "temperature", "rain", "climate",
#         "మౌసమ్", "వాతావరణం", "తాపోగ్రత", "వర్షం",
#         "मौसम", "तापमान", "बारिश", "जलवायु"
#     ]
#     is_weather_query = any(word.lower() in query_text.lower() for word in weather_keywords)

#     # ---------------- WEATHER HANDLING ----------------
#     weather_date = extract_weather_date(query_text) if is_weather_query else None

#     if is_weather_query and lat is not None and lon is not None:
#         weather_data = get_weather(lat, lon, weather_date)
#         if weather_data:
#             date_str = weather_date if weather_date else "today"
#             weather_tense = get_weather_tense(weather_date)
#             if weather_tense == "past":
#                 day_phrase = "on that day"
#             elif weather_tense == "today":
#                 day_phrase = "today"
#             else:
#                 day_phrase = "on the day you asked"

#             weather_prompt = (
#                 f"Tell a farmer about the weather in simple language for {day_phrase}. "
#                 f"Max temp: {weather_data.get('temperature_max', weather_data.get('temperature'))}°C, "
#                 f"Min temp: {weather_data.get('temperature_min', 'N/A')}°C, "
#                 f"Condition: {weather_data['condition']}, "
#                 f"Precipitation: {weather_data.get('precipitation', 'N/A')}mm, "
#                 f"Wind speed: {weather_data['windspeed']} km/h. "
#                 "Give practical farming advice in 2–3 sentences. "
#                 "Do NOT mention the actual date; instead use the phrase provided above. "
#                 f"Write the response in {weather_tense} tense."
#             )

#             try:
#                 client = Groq(api_key=GROQ_API_KEY)
#                 chat_completion = client.chat.completions.create(
#                     messages=[
#                         {"role": "system", "content": "You are a helpful agricultural advisor."},
#                         {"role": "user", "content": weather_prompt}
#                     ],
#                     model="llama-3.3-70b-versatile",
#                     temperature=0.7,
#                     max_tokens=200,
#                     top_p=1,
#                 )
#                 return chat_completion.choices[0].message.content
#             except:
#                 return f"Weather on {date_str}: {weather_data.get('temperature')}°C, {weather_data['condition']}."
#         else:
#             return "I couldn't fetch the weather information right now. Please try again."
    
#     # ---------------- GENERAL AI HANDLING ----------------
#     if not GROQ_API_KEY:
#         raise Exception("GROQ_API_KEY not set.")
    
#     try:
#         client = Groq(api_key=GROQ_API_KEY)
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a helpful agricultural advisor for farmers in India. "
#                         "Provide practical, accurate advice in simple language. "
#                         "Keep responses concise (2–4 sentences). "
#                         "Focus on Indian farming practices, crops, weather conditions, "
#                         "government schemes (PM-KISAN, PMFBY), and local solutions."
#                     )
#                 },
#                 {"role": "user", "content": query_text}
#             ],
#             model="llama-3.3-70b-versatile",
#             temperature=0.7,
#             max_tokens=300,
#             top_p=1,
#         )
#         return chat_completion.choices[0].message.content
#     except Exception as e:
#         raise Exception(f"Groq API error: {str(e)}")


# # ---------------------------
# # Main Pipeline
# # ---------------------------

# def handle_farmer_query(audio_file_path, farmer_lang="te", gender="female", speed=1.0, lat=None, lon=None):
#     """Main pipeline to process farmer query"""
#     # Step 1: ASR using Bhashini
#     print(f"\n🎧 Processing audio in {API_CONFIG[farmer_lang]['NAME']} using Bhashini ASR...")
#     recognized_text = asr(audio_file_path, farmer_lang)
#     print(f"✓ Recognized: {recognized_text}")

#     # Step 2: Translate to English for AI processing using Bhashini
#     print("\n🔄 Translating to English for AI using Bhashini...")
#     text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
#     print(f"✓ Translated: {text_for_ai}")

#     # Step 3: Get AI / Weather answer (in English)
#     print("\n🤖 Getting AI response...")
#     ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon)
#     print(f"✓ AI Response: {ai_answer_en}")

#     # Step 4: Translate back to farmer's language using Bhashini
#     print(f"\n🔄 Translating back to {API_CONFIG[farmer_lang]['NAME']} using Bhashini...")
#     answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
#     print(f"✓ Translated Answer: {answer_local}")
    
#     # Step 5: Generate TTS using Bhashini
#     print("\n🔊 Generating audio response using Bhashini TTS...")
#     audio_filename = tts(answer_local, farmer_lang, gender, speed)
#     print(f"✓ Audio saved: {audio_filename}")

#     return {
#         "success": True,
#         "query_text": recognized_text,
#         "answer_text": answer_local,
#         "audio_file": f"outputs/{audio_filename}"  # Include the folder path
#     }


# # ---------------------------
# # Routes
# # ---------------------------

# @app.post("/handle_farmer_query")
# async def handle_query(
#     file: UploadFile,
#     lang: str = Form("te"),
#     gender: str = Form("male"),
#     speed: float = Form(1.0),
#     lat: str = Form(None),
#     lon: str = Form(None)
# ):
#     # Save uploaded file to UPLOAD_FOLDER
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     try:
#         with open(file_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)
#     finally:
#         await file.close()

#     # Call the main pipeline
#     try:
#         result = handle_farmer_query(
#             audio_file_path=file_path,
#             farmer_lang=lang,
#             gender=gender,
#             speed=speed,
#             lat=lat,
#             lon=lon
#         )
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"success": False, "reply": str(e)})

#     return JSONResponse(content=result)


# @app.get("/outputs/{filename}")
# async def serve_output_audio(filename: str):
#     """Serve generated audio files from outputs folder"""
#     file_path = os.path.join(OUTPUT_FOLDER, filename)
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="audio/wav")
#     else:
#         raise HTTPException(status_code=404, detail="File not found")


# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)


from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import requests
from datetime import datetime
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
# Config: Language-specific APIs
# ---------------------------

# Bhashini Configuration
BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# Groq API Configuration
GROQ_API_KEY = "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"


# Config: Comprehensive Language-specific settings
# ASR/TTS Services are chosen based on the most robust multilingual models available in the tables.
# TTS Fallback: Bhashini/IITM/TTS is used for languages without a specific AI4Bharat coqui model.
API_CONFIG = {
    # English (Specific ASR, Misc TTS)
    "en": {"NAME": "English", "CODE": "en", "ASR_SERVICE": "ai4bharat/whisper-medium-en--gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"},

    # Indo-Aryan Group (Multilingual ASR & TTS)
    "hi": {"NAME": "Hindi (हिंदी)", "CODE": "hi", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "bn": {"NAME": "Bengali (বাংলা)", "CODE": "bn", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "mr": {"NAME": "Marathi (मराठी)", "CODE": "mr", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "gu": {"NAME": "Gujarati (ગુજરાતી)", "CODE": "gu", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "or": {"NAME": "Odia (ଓଡ଼ିଆ)", "CODE": "or", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "pa": {"NAME": "Punjabi (ਪੰਜਾਬੀ)", "CODE": "pa", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"},
    "as": {"NAME": "Assamese (অসমীয়া)", "CODE": "as", "ASR_SERVICE": "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"}, # Note: Using Indo-Aryan group service IDs
    
    # Dravidian Group (Multilingual ASR & TTS)
    "te": {"NAME": "Telugu (తెలుగు)", "CODE": "te", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "kn": {"NAME": "Kannada (ಕನ್ನಡ)", "CODE": "kn", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "ta": {"NAME": "Tamil (தமிழ்)", "CODE": "ta", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    "ml": {"NAME": "Malayalam (മലയാളം)", "CODE": "ml", "ASR_SERVICE": "ai4bharat/conformer-multilingual-dravidian-gpu--t4", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"},
    
    # Other Scheduled Languages (Using general Bhashini multilingual ASR and IITM TTS)
    "ur": {"NAME": "Urdu (اُردُو)", "CODE": "ur", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sa": {"NAME": "Sanskrit (संस्कृतम्)", "CODE": "sa", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "brx": {"NAME": "Bodo (बर')", "CODE": "brx", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "ai4bharat/indic-tts-coqui-misc-gpu--t4"}, # Bodo TTS is in Misc group
    "doi": {"NAME": "Dogri (डोगरी)", "CODE": "doi", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "ks": {"NAME": "Kashmiri (کٲشُر)", "CODE": "ks", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "gom": {"NAME": "Goan Konkani (कोंकणी)", "CODE": "gom", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "mai": {"NAME": "Maithili (मैथिली)", "CODE": "mai", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "ne": {"NAME": "Nepali (नेपाली)", "CODE": "ne", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sat": {"NAME": "Santali (ᱥᱟᱱᱛᱟᱲᱤ)", "CODE": "sat", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
    "sd": {"NAME": "Sindhi (سنڌي)", "CODE": "sd", "ASR_SERVICE": "bhashini/ai4bharat/conformer-multilingual-asr", "TTS_SERVICE": "Bhashini/IITM/TTS"},
}

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
            # Added error detail for better debugging
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
            
            # Save audio to OUTPUT_FOLDER (not root directory)
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
    except:
        return None


def get_ai_answer(query_text, farmer_lang="te", lat=None, lon=None, state="Karnataka"):
    """Get intelligent answer using Groq API or fetch weather based on query"""
    # Check for weather query (keywords in multiple languages)
    weather_keywords = [
        "weather", "temperature", "rain", "climate",
        "మౌసమ్", "వాతావరణం", "తాపోగ్రత", "వర్షం",
        "मौसम", "तापमान", "बारिश", "जलवायु"
    ]
    is_weather_query = any(word.lower() in query_text.lower() for word in weather_keywords)

    # ---------------- WEATHER HANDLING ----------------
    weather_date = extract_weather_date(query_text) if is_weather_query else None

    if is_weather_query and lat is not None and lon is not None:
        weather_data = get_weather(lat, lon, weather_date)
        if weather_data:
            date_str = weather_date if weather_date else "today"
            weather_tense = get_weather_tense(weather_date)
            if weather_tense == "past":
                day_phrase = "on that day"
            elif weather_tense == "today":
                day_phrase = "today"
            else:
                day_phrase = "on the day you asked"

            weather_prompt = (
                f"Tell a farmer about the weather in simple language for {day_phrase}. "
                f"Max temp: {weather_data.get('temperature_max', weather_data.get('temperature'))}°C, "
                f"Min temp: {weather_data.get('temperature_min', 'N/A')}°C, "
                f"Condition: {weather_data['condition']}, "
                f"Precipitation: {weather_data.get('precipitation', 'N/A')}mm, "
                f"Wind speed: {weather_data['windspeed']} km/h. "
                "Give practical farming advice in 2–3 sentences. "
                "Do NOT mention the actual date; instead use the phrase provided above. "
                f"Write the response in {weather_tense} tense."
            )

            try:
                client = Groq(api_key=GROQ_API_KEY)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful agricultural advisor."},
                        {"role": "user", "content": weather_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=200,
                    top_p=1,
                )
                return chat_completion.choices[0].message.content
            except:
                return f"Weather on {date_str}: {weather_data.get('temperature')}°C, {weather_data['condition']}."
        else:
            return "I couldn't fetch the weather information right now. Please try again."
    
    # ---------------- GENERAL AI HANDLING ----------------
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not set.")
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful agricultural advisor for farmers in India. "
                        "Provide practical, accurate advice in simple language. "
                        "Keep responses concise (2–4 sentences). "
                        "Focus on Indian farming practices, crops, weather conditions, "
                        "government schemes (PM-KISAN, PMFBY), and local solutions."
                    )
                },
                {"role": "user", "content": query_text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300,
            top_p=1,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")


# ---------------------------
# Main Pipeline
# ---------------------------

# UPDATED: Added 'state' parameter to the definition
def handle_farmer_query(audio_file_path, farmer_lang="te", gender="female", speed=1.0, lat=None, lon=None, state=None):
    """Main pipeline to process farmer query"""
    # Step 1: ASR using Bhashini
    print(f"\n🎧 Processing audio in {API_CONFIG[farmer_lang]['NAME']} using Bhashini ASR...")
    recognized_text = asr(audio_file_path, farmer_lang)
    print(f"✓ Recognized: {recognized_text}")

    # Step 2: Translate to English for AI processing using Bhashini
    print("\n🔄 Translating to English for AI using Bhashini...")
    text_for_ai = mt(recognized_text, source_lang=farmer_lang, target_lang="en")
    print(f"✓ Translated: {text_for_ai}")

    # Step 3: Get AI / Weather answer (in English)
    print("\n🤖 Getting AI response...")
    # UPDATED: Pass 'state' to get_ai_answer
    ai_answer_en = get_ai_answer(text_for_ai, farmer_lang, lat, lon, state) 
    print(f"✓ AI Response: {ai_answer_en}")

    # Step 4: Translate back to farmer's language using Bhashini
    print(f"\n🔄 Translating back to {API_CONFIG[farmer_lang]['NAME']} using Bhashini...")
    answer_local = mt(ai_answer_en, source_lang="en", target_lang=farmer_lang)
    print(f"✓ Translated Answer: {answer_local}")
    
    # Step 5: Generate TTS using Bhashini
    print("\n🔊 Generating audio response using Bhashini TTS...")
    audio_filename = tts(answer_local, farmer_lang, gender, speed)
    print(f"✓ Audio saved: {audio_filename}")

    return {
        "success": True,
        "query_text": recognized_text,
        "answer_text": answer_local,
        "audio_file": f"outputs/{audio_filename}"  # Include the folder path
    }


# ---------------------------
# Routes
# ---------------------------

@app.post("/handle_farmer_query")
async def handle_query(
    file: UploadFile,
    lang: str = Form("te"),
    gender: str = Form("male"),
    speed: float = Form(1.0),
    lat: str = Form(None),
    lon: str = Form(None),
    state: str = Form(None) # ADDED: Receiving 'state' from the frontend
):
    # Save uploaded file to UPLOAD_FOLDER
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        await file.close()

    # Call the main pipeline
    try:
        result = handle_farmer_query(
            audio_file_path=file_path,
            farmer_lang=lang,
            gender=gender,
            speed=speed,
            lat=lat,
            lon=lon,
            state=state # ADDED: Passing 'state' to the pipeline
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "reply": str(e)})

    return JSONResponse(content=result)


@app.get("/outputs/{filename}")
async def serve_output_audio(filename: str):
    """Serve generated audio files from outputs folder"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="File not found")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)