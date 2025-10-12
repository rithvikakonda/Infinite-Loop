# from fastapi import FastAPI, Form, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from pydub import AudioSegment
# import requests, os, io, uuid, json, base64, re

# app = FastAPI()

# API_CONFIG_PATH = "model_config.json"

# # Mount static folder for saving audio if needed
# if not os.path.exists("static"):
#     os.makedirs("static")
# app.mount("/static", StaticFiles(directory="static"), name="static")


# def get_api_info(model, source_lang=None, target_lang=None):
#     """Fetch API endpoint and access token from JSON config."""
#     with open(API_CONFIG_PATH, "r") as f:
#         configs = json.load(f)

#     model = model.lower()
#     src = (source_lang or "").lower()
#     tgt = (target_lang or "").lower()

#     for cfg in configs:
#         if cfg.get("model_type", "").lower() != model:
#             continue
#         cfg_source = (cfg.get("source_language") or "").lower()
#         cfg_target = (cfg.get("target_language") or "").lower()
#         if model == "tts" and cfg_source == tgt:
#             return cfg["api_url"], cfg["access_token"]
#     raise ValueError(f"No API config found for model={model}, target={target_lang}")


# def split_text_for_tts(text, max_words=30):
#     """Split text into manageable chunks for TTS."""
#     text = re.sub(r'\s+', ' ', text.strip())
#     words = text.split()
#     return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


# # @app.post("/text-to-speech")
# # async def text_to_speech(
# #     text: str = Form(...),
# #     target_lang: str = Form(...),
# #     tts_gender: str = Form("female")
# # ):
# #     try:
# #         print(f"Received text for TTS: {text[:60]}... | Lang: {target_lang} | Gender: {tts_gender}")

# #         # Get TTS API info
# #         TTS_API_ENDPOINT, TTS_ACCESS_TOKEN = get_api_info("tts", target_lang=target_lang)
# #         headers = {"access-token": TTS_ACCESS_TOKEN, "Content-Type": "application/json"}

# #         # Split long text into chunks
# #         chunks = split_text_for_tts(text, max_words=30)
# #         print(f"Text split into {len(chunks)} chunks for TTS.")

# #         audio_segments = []

# #         # Process each chunk
# #         for chunk in chunks:
# #             payload = {"text": chunk, "gender": tts_gender}
# #             response = requests.post(TTS_API_ENDPOINT, headers=headers, json=payload, verify=False)
# #             data = response.json()

# #             if data.get("status") != "success":
# #                 raise HTTPException(status_code=500, detail=f"TTS Error: {data.get('error')}")

# #             tts_url = data["data"]["s3_url"]
# #             audio_bytes = requests.get(tts_url).content
# #             segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
# #             audio_segments.append(segment)

# #         # Merge all audio segments
# #         final_audio = sum(audio_segments)
# #         audio_buffer = io.BytesIO()
# #         final_audio.export(audio_buffer, format="wav")
# #         audio_buffer.seek(0)

# #         # Convert to base64
# #         audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

# #         return JSONResponse({
# #             "translated_text": text,
# #             "audio_base64": audio_base64,
# #             "tts_chunks": len(audio_segments)
# #         })

# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))
# @app.post("/text-to-speech")
# async def text_to_speech(
#     text: str = Form(...),
#     target_lang: str = Form(...),
#     tts_gender: str = Form("female")
# ):
#     try:
#         print(f"Received text for TTS: {text[:60]}... | Lang: {target_lang} | Gender: {tts_gender}")

#         # Get TTS API info
#         TTS_API_ENDPOINT, TTS_ACCESS_TOKEN = get_api_info("tts", target_lang=target_lang)
#         print("TTS endpoint:", TTS_API_ENDPOINT)
#         print("TTS token:", TTS_ACCESS_TOKEN[:10] + "..." if TTS_ACCESS_TOKEN else "None")

#         headers = {"access-token": TTS_ACCESS_TOKEN, "Content-Type": "application/json"}

#         chunks = split_text_for_tts(text, max_words=30)
#         print(f"Text split into {len(chunks)} chunks for TTS.")

#         audio_segments = []

#         for chunk in chunks:
#             payload = {"text": chunk, "gender": tts_gender}
#             print(f"Sending chunk to TTS API: {payload}")

#             response = requests.post(TTS_API_ENDPOINT, headers=headers, json=payload, verify=False)
#             print("Response status:", response.status_code)
#             print("Response text:", response.text[:300])

#             data = response.json()
#             if data.get("status") != "success":
#                 raise HTTPException(status_code=500, detail=f"TTS Error: {data.get('error')}")

#             tts_url = data["data"]["s3_url"]
#             print("Audio URL:", tts_url)

#             audio_bytes = requests.get(tts_url).content
#             segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
#             audio_segments.append(segment)

#         final_audio = sum(audio_segments)
#         audio_buffer = io.BytesIO()
#         final_audio.export(audio_buffer, format="wav")
#         audio_buffer.seek(0)

#         audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

#         return JSONResponse({
#             "translated_text": text,
#             "audio_base64": audio_base64,
#             "tts_chunks": len(audio_segments)
#         })

#     except Exception as e:
#         import traceback
#         print("TTS ERROR:", traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))


# # --- CORS ---
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["http://localhost:9000"],  # frontend origin
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )


from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import requests, os, io, uuid, json, base64, re

app = FastAPI()

# ---------------- CONFIG ----------------
API_CONFIG_PATH = "model_config.json"

# Mount static folder for saving audio files if needed
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- UTILS ----------------
def get_api_info(model, source_lang=None, target_lang=None):
    """Fetch API endpoint and access token from JSON config."""
    with open(API_CONFIG_PATH, "r") as f:
        configs = json.load(f)

    model = model.lower()
    src = (source_lang or "").lower()
    tgt = (target_lang or "").lower()

    for cfg in configs:
        if cfg.get("model_type", "").lower() != model:
            continue
        cfg_source = (cfg.get("source_language") or "").lower()
        cfg_target = (cfg.get("target_language") or "").lower()

        # ✅ For TTS we match the target_lang
        if model == "tts" and cfg_target == tgt:
            return cfg["api_url"], cfg["access_token"]

    raise ValueError(f"No API config found for model={model}, target={target_lang}")


def split_text_for_tts(text, max_words=30):
    """Split text into smaller chunks to avoid TTS API limits."""
    text = re.sub(r'\s+', ' ', text.strip())
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


# ---------------- API ROUTE ----------------
@app.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    target_lang: str = Form(...),
    tts_gender: str = Form("female")
):
    try:
        print(f"🎤 Received TTS request: '{text[:50]}...' | Lang: {target_lang} | Gender: {tts_gender}")

        # Step 1: Get TTS API endpoint and token
        TTS_API_ENDPOINT, TTS_ACCESS_TOKEN = get_api_info("tts", target_lang=target_lang)
        TTS_HEADERS = {"access-token": TTS_ACCESS_TOKEN, "Content-Type": "application/json"}

        # Step 2: Split long text into chunks
        chunks = split_text_for_tts(text, max_words=30)
        print(f"🧩 Text split into {len(chunks)} chunks for TTS.")

        audio_segments = []

        # Step 3: Send each chunk to the TTS API
        for chunk in chunks:
            payload = {"text": chunk, "gender": tts_gender}
            response = requests.post(TTS_API_ENDPOINT, headers=TTS_HEADERS, json=payload, verify=False)
            data = response.json()

            if data.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"TTS Error: {data.get('error')}")

            # Download audio
            tts_url = data["data"]["s3_url"]
            print(f"✅ TTS chunk generated: {tts_url}")
            audio_bytes = requests.get(tts_url).content
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            audio_segments.append(audio_segment)

        # Step 4: Merge all TTS chunks
        final_audio = sum(audio_segments)
        audio_buffer = io.BytesIO()
        final_audio.export(audio_buffer, format="wav")
        audio_buffer.seek(0)

        # Step 5: Encode to base64 for API response
        audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

        return JSONResponse({
            "input_text": text,
            "audio_base64": audio_base64,
            "tts_chunks": len(audio_segments)
        })

    except Exception as e:
        print(f"❌ TTS ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
