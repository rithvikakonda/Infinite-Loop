from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, io, uuid, json, re, subprocess
from PIL import Image
from pdf2image import convert_from_path
import requests

# Optional local OCR fallback
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except Exception:
    PYTESSERACT_AVAILABLE = False

# -------------------------------
# CONFIGURATION
# -------------------------------
MODELS_FILE = "filled_megathon_models_68ea6053b93e3bec901fd8c5_1760201701.json"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

HARDCODED_OCR_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJ1c2VyX2lkIjoiNjhlYTVmZWRiOTNlM2JlYzkwMWZkOGMzIiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ."
    "nreIT2AkCYQOawaftY7vRvEA4sgDGWQ7uyj-oI-xxz0"
)

# -------------------------------
# FASTAPI APP
# -------------------------------
app = FastAPI(title="Dynamic OCR + Translation API")

# ✅ CORS middleware (must be here, right after app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; replace with frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------------
# BASIC UTILITIES
# -------------------------------
def normalize_text(text: str) -> str:
    return text.replace("\n", " ").strip()

def load_models(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Models file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_ocr_model(models, source_lang: str):
    for m in models:
        if m.get("model_type") == "ocr":
            model_name = m.get("model_name", "")
            if "-" in model_name:
                lang = model_name.split("-")[-1].strip().lower()
                if lang == source_lang.lower():
                    return m
    raise ValueError(f"No OCR model found for language: {source_lang}")

def find_mt_model(models, source_lang: str, target_lang: str):
    for m in models:
        if m.get("model_type") == "mt":
            src = m.get("source_language", "").lower()
            tgt = m.get("target_language", "").lower()
            if src == source_lang.lower() and tgt == target_lang.lower():
                return m
    raise ValueError(f"No MT model found for {source_lang} → {target_lang}")

# -------------------------------
# OCR / Translation CALLS
# -------------------------------
def call_canvas_ocr(image_bytes: bytes, ocr_url: str, ocr_token: str) -> str:
    headers = {"access-token": ocr_token}
    files = {"file": ("image.jpeg", image_bytes, "image/jpeg")}
    resp = requests.post(ocr_url, headers=headers, files=files, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"OCR API error: {resp.status_code} {resp.text}")
    data = resp.json()
    if "data" in data and isinstance(data["data"], dict):
        if "decoded" in data["data"]:
            return data["data"]["decoded"]
        elif "decoded_text" in data["data"]:
            return data["data"]["decoded_text"]
    raise RuntimeError(f"Unexpected OCR response: {data}")

def local_ocr_fallback(image_bytes: bytes) -> str:
    if not PYTESSERACT_AVAILABLE:
        raise RuntimeError("pytesseract not installed")
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return pytesseract.image_to_string(image, lang="eng")

def smart_chunk_text(text, max_words=50):
    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current_chunk, current_word_count = [], [], 0

    for sentence in sentences:
        if not sentence.strip():
            continue
        words_in_sentence = sentence.split()
        sentence_word_count = len(words_in_sentence)
        if sentence_word_count > max_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk, current_word_count = [], 0
            for i in range(0, len(words_in_sentence), max_words):
                chunks.append(" ".join(words_in_sentence[i:i+max_words]))
        else:
            if current_word_count + sentence_word_count > max_words and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk, current_word_count = [sentence], sentence_word_count
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def call_bhashini_mt(recognized_text: str, mt_url: str, mt_token: str) -> str:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "access-token": mt_token,
    }
    translated_chunks = []
    chunks = smart_chunk_text(recognized_text, 50)
    for chunk in chunks:
        payload = {"input_text": chunk}
        response = requests.post(mt_url, headers=headers, json=payload, verify=False)
        if response.status_code != 200:
            raise RuntimeError(f"MT HTTP error: {response.status_code} {response.text}")
        data = response.json()
        if data.get("status") != "success":
            raise RuntimeError(f"MT Error: {data.get('error', 'Unknown error')}")
        translated_chunks.append(data["data"]["output_text"])
    return " ".join(translated_chunks)

# -------------------------------
# FILE PROCESSING
# -------------------------------
def convert_to_pdf(input_path: str, output_dir: str) -> str:
    result = subprocess.run(
        ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )
    base = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, base + '.pdf')

def process_image_file(image_bytes: bytes, ocr_model, mt_model, ocr_token: str):
    try:
        extracted_text = call_canvas_ocr(image_bytes, ocr_model["api_url"], ocr_token)
    except Exception:
        extracted_text = local_ocr_fallback(image_bytes)
    clean_text = normalize_text(extracted_text)
    translated_text = call_bhashini_mt(clean_text, mt_model["api_url"], mt_model["access_token"])
    filename_base = uuid.uuid4().hex
    text_out_path = os.path.join(OUT_DIR, f"{filename_base}_translated.txt")
    with open(text_out_path, "w", encoding="utf-8") as f:
        f.write(translated_text)
    return extracted_text, clean_text, translated_text, text_out_path

def process_pdf_file(file_path: str, ocr_model, mt_model, ocr_token: str):
    pages = convert_from_path(file_path, dpi=300)
    all_translated_text = []
    for page_image in pages:
        image_bytes_io = io.BytesIO()
        page_image.save(image_bytes_io, format="JPEG")
        image_bytes = image_bytes_io.getvalue()
        try:
            extracted_text = call_canvas_ocr(image_bytes, ocr_model["api_url"], ocr_token)
        except Exception:
            extracted_text = local_ocr_fallback(image_bytes)
        clean_text = normalize_text(extracted_text)
        translated_text = call_bhashini_mt(clean_text, mt_model["api_url"], mt_model["access_token"])
        all_translated_text.append(translated_text)
    filename_base = uuid.uuid4().hex
    text_out_path = os.path.join(OUT_DIR, f"{filename_base}_document.txt")
    with open(text_out_path, "w", encoding="utf-8") as f:
        for page_text in all_translated_text:
            f.write(page_text + "\n\n")
    return all_translated_text, text_out_path

# -------------------------------
# ENDPOINTS
# -------------------------------
@app.get("/")
def root():
    return {"message": "OCR + Translation API is running. Use POST /translate/ to upload files."}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.post("/document-translator/")
async def translate_file(
    file: UploadFile,
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    try:
        models = load_models(MODELS_FILE)
        ocr_model = find_ocr_model(models, source_lang)
        mt_model = find_mt_model(models, source_lang, target_lang)
        ocr_token = ocr_model.get("access_token") or HARDCODED_OCR_TOKEN
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    temp_filename = os.path.join(OUT_DIR, uuid.uuid4().hex + "_" + file.filename)
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    ext = os.path.splitext(file.filename)[-1].lower()

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            with open(temp_filename, "rb") as f:
                image_bytes = f.read()
            extracted_text, clean_text, translated_text, out_path = process_image_file(
                image_bytes, ocr_model, mt_model, ocr_token
            )
            return JSONResponse({
                "status": "success",
                "type": "image",
                "extracted_text": extracted_text,
                "normalized_text": clean_text,
                "translated_text": translated_text,
                "output_file": os.path.basename(out_path)
            })

        elif ext == '.pdf':
            all_translated_text, out_path = process_pdf_file(temp_filename, ocr_model, mt_model, ocr_token)
            return JSONResponse({
                "status": "success",
                "type": "pdf",
                "translated_pages": all_translated_text,
                "output_file": os.path.basename(out_path)
            })

        elif ext in ['.txt', '.csv', '.html', '.xml', '.rtf']:
            with open(temp_filename, "r", encoding="utf-8") as f:
                raw_text = normalize_text(f.read())
            translated_text = call_bhashini_mt(raw_text, mt_model["api_url"], mt_model["access_token"])
            out_path = os.path.join(OUT_DIR, uuid.uuid4().hex + "_translated.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(translated_text)
            return JSONResponse({
                "status": "success",
                "type": "text",
                "original_text": raw_text,
                "translated_text": translated_text,
                "output_file": os.path.basename(out_path)
            })

        elif ext in ['.doc', '.docx', '.ppt', '.pptx', '.odt', '.odp']:
            converted_pdf = convert_to_pdf(temp_filename, OUT_DIR)
            all_translated_text, out_path = process_pdf_file(converted_pdf, ocr_model, mt_model, ocr_token)
            return JSONResponse({
                "status": "success",
                "type": "document",
                "translated_pages": all_translated_text,
                "output_file": os.path.basename(out_path)
            })

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))