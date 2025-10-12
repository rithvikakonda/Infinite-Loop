from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from moviepy.editor import VideoFileClip
from pydub import AudioSegment, silence
import requests, os, tempfile, io, uuid, json
import re
import base64
app = FastAPI()

# Path to your JSON configuration
API_CONFIG_PATH = "model_config.json"

MAX_ASR_DURATION = 20 * 1000  # 20 seconds in milliseconds

# Mount static folder for TTS output
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_api_info(model, source_lang=None, target_lang=None):
    """
    Fetch API endpoint and access token from JSON config.
    - ASR: compare only target_lang.
    - MT, TTS: compare both source_lang and target_lang.
    """
    with open(API_CONFIG_PATH, "r") as f:
        configs = json.load(f)

    model = model.lower()

    for cfg in configs:
        if cfg.get("model_type", "").lower() != model:
            continue
        cfg_source = (cfg.get("source_language") or "").lower()
        cfg_target = (cfg.get("target_language") or "").lower()
        src = (source_lang or "").lower()
        tgt = (target_lang or "").lower()
        if model == "asr" and cfg_source == src:
            print(cfg_source, src, cfg_target, tgt)
            print(cfg["api_url"], cfg["access_token"])
            return cfg["api_url"], cfg["access_token"]
        elif model == "mt" and cfg_source == src and cfg_target == tgt:
            print(cfg_source, src, cfg_target, tgt)
            print(cfg["api_url"], cfg["access_token"])
            return cfg["api_url"], cfg["access_token"]
        elif model == "tts" and cfg_source == tgt:
            print(cfg["api_url"], cfg["access_token"])
            return cfg["api_url"], cfg["access_token"]
    raise ValueError(f"No API config found for model={model}, source={source_lang}, target={target_lang}")

def split_on_silence(audio_path, min_silence_len=500, silence_thresh=-40):
    """Split audio on silence."""
    audio = AudioSegment.from_wav(audio_path)
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=250
    )
    chunk_paths = []
    for i, chunk in enumerate(chunks):
        chunk_path = f"{audio_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)
    return chunk_paths


def call_asr(audio_path, ASR_ACCESS_TOKEN,ASR_API_ENDPOINT):
    """Send audio chunk to ASR API and return recognized text."""
    headers = {"access-token": ASR_ACCESS_TOKEN}
    with open(audio_path, "rb") as f:
        files = {"audio_file": (os.path.basename(audio_path), f, "audio/wav")}
        response = requests.post(ASR_API_ENDPOINT, files=files, headers=headers, verify=False)
    data = response.json()
    if data.get("status") != "success":
        raise Exception(f"ASR Error: {data.get('error')}")
    print("Asr done!")
    return data["data"]["recognized_text"]


def split_text_into_chunks(text, max_words=50):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


def split_text_for_tts(text, max_words=30):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def smart_chunk_text(text, max_words=50):
    """
    Split text into chunks of <= max_words without breaking sentences.
    If adding a sentence would exceed max_words, complete the current chunk
    and start a new one with that sentence.
    """
    # Normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        words_in_sentence = sentence.split()
        sentence_word_count = len(words_in_sentence)
        
        print(f"Sentence: {sentence_word_count} words | Current total: {current_word_count}")
        
        # If single sentence is too long (> max_words), handle separately
        if sentence_word_count > max_words:
            # Save current chunk first if it exists
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                print(f"✓ Chunk completed before long sentence: {current_word_count} words")
                current_chunk = []
                current_word_count = 0
            
            # Split the long sentence
            words = sentence.split()
            for i in range(0, len(words), max_words):
                end = min(i + max_words, len(words))
                sub_chunk = " ".join(words[i:end])
                chunks.append(sub_chunk)
                print(f"✓ Long sentence sub-chunk: {len(sub_chunk.split())} words")
        
        else:
            # Check if adding this sentence would exceed max_words
            if current_word_count + sentence_word_count > max_words and current_chunk:
                # Save current chunk and start new one with this sentence
                chunks.append(" ".join(current_chunk))
                print(f"✓ Chunk completed: {current_word_count} words (would become {current_word_count + sentence_word_count} with next sentence)")
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
                print(f"Added to chunk: {sentence_word_count} words, total: {current_word_count}")
    
    # Add any remaining content
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        print(f"✓ Final chunk: {current_word_count} words")
    
    return chunks


@app.post("/video-to-translate-and-speak")
async def video_to_translate_and_speak(
    video_file: UploadFile,
    target_lang: str = Form(...),
    tts_gender: str = Form("female"),
    source_lang: str = Form("en")
):
    try:
        print(f"Received video: {video_file.filename}, source_lang: {source_lang}, target_lang: {target_lang}")
        # Step 1: Save uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as temp_video:
            temp_video.write(await video_file.read())
            video_path = temp_video.name

        # Step 2: Extract audio as WAV
        audio_path = os.path.splitext(video_path)[0] + ".wav"
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, codec="pcm_s16le")
        clip.close()
        audio_chunks = split_on_silence(audio_path)
        print(f"Audio split into {len(audio_chunks)} chunks.")
        # Step 4: Call ASR on each chunk
        ASR_API_ENDPOINT, ASR_ACCESS_TOKEN = get_api_info("asr", source_lang=source_lang)
        recognized_texts = [call_asr(chunk,ASR_ACCESS_TOKEN,ASR_API_ENDPOINT) for chunk in audio_chunks]
        for chunk in audio_chunks:
            os.remove(chunk)  # cleanup
        final_text = " ".join(recognized_texts)
        print(f"Final recognized text: {final_text}")
        # Step 5: Translate text in chunks
        MT_API_ENDPOINT, MT_ACCESS_TOKEN = get_api_info("mt", source_lang=source_lang, target_lang=target_lang)
        MT_HEADERS = {"access-token": MT_ACCESS_TOKEN, "Content-Type": "application/json"}
        chunks = smart_chunk_text(final_text, max_words=50)

        translated_chunks = []
        for chunk in chunks:
            mt_payload = {"input_text": chunk}
            mt_response = requests.post(MT_API_ENDPOINT, headers=MT_HEADERS, json=mt_payload, verify=False)
            mt_data = mt_response.json()
            if mt_data.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"MT Error: {mt_data.get('error')}")
            translated_chunks.append(mt_data["data"]["output_text"])
        translated_text = " ".join(translated_chunks)
        print(f"Translated text: {translated_text}")
        # Step 6: TTS
        TTS_API_ENDPOINT, TTS_ACCESS_TOKEN = get_api_info("tts", target_lang=target_lang)
        TTS_HEADERS = {"access-token": TTS_ACCESS_TOKEN, "Content-Type": "application/json"}
        tts_audio_segments = []
        for chunk in split_text_for_tts(translated_text, max_words=30):
            tts_payload = {"text": chunk, "gender": tts_gender}
            tts_response = requests.post(TTS_API_ENDPOINT, headers=TTS_HEADERS, json=tts_payload, verify=False)
            tts_data = tts_response.json()
            if tts_data.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"TTS Error: {tts_data.get('error')}")
            tts_url = tts_data["data"]["s3_url"]
            audio_bytes = requests.get(tts_url).content
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            tts_audio_segments.append(audio_segment)

        # Merge TTS segments
        final_audio = sum(tts_audio_segments)
        final_audio_filename = f"{uuid.uuid4().hex}_final_tts.wav"
        final_audio_path = os.path.join("static", final_audio_filename)
        final_audio.export(final_audio_path, format="wav")

        base_url = "http://127.0.0.1:8001"
        final_audio_url = f"{base_url}/static/{final_audio_filename}"

# ... keep everything same above

# Merge TTS segments
        final_audio = sum(tts_audio_segments)
        audio_buffer = io.BytesIO()
        final_audio.export(audio_buffer, format="wav")
        audio_buffer.seek(0)

        # Convert to base64
        audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

        return JSONResponse({
            "source_text": final_text,
            "translated_text": translated_text,
            "audio_base64": audio_base64,   # 🔹 Send base64 instead of file
            "tts_chunks": len(tts_audio_segments)
        })

        # return JSONResponse({
        #     "source_text": final_text,
        #     "translated_text": translated_text,
        #     "merged_audio_file": final_audio_url,
        #     "tts_chunks": len(tts_audio_segments)
        # })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
