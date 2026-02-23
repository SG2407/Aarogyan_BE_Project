
import io
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import tesserocr
import requests
from app.core.config import settings
from supabase import create_client, Client
import openai

router = APIRouter()

@router.get("/list")
def list_documents(user_id: str = Depends(lambda: "demo-user-id")):
    # Fetch all documents for the user
    res = supabase.table("medical_documents").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    docs = res.data if hasattr(res, 'data') else res.get('data', [])
    return {"documents": docs}


@router.get("/{doc_id}")
def get_document(doc_id: str, user_id: str = Depends(lambda: "demo-user-id")):
    # Fetch a specific document by id for the user
    res = supabase.table("medical_documents").select("*").eq("id", doc_id).eq("user_id", user_id).single().execute()
    doc = res.data if hasattr(res, 'data') else res.get('data', None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

# Initialize Supabase client
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

BUCKET_NAME = "medical_documents"
MAX_FILE_SIZE_MB = 5
ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]


def compress_image(image: Image.Image, max_size_mb=5) -> bytes:
    # Compress image to fit under max_size_mb
    quality = 85
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)
    while output.tell() > max_size_mb * 1024 * 1024 and quality > 10:
        quality -= 5
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality)
    return output.getvalue()


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return tesserocr.image_to_text(image)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    # Save PDF to temp file, use tesseract via poppler-utils (pdftoppm)
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf.flush()
        # Convert PDF pages to images
        from pdf2image import convert_from_path
        images = convert_from_path(temp_pdf.name)
        text = ""
        for img in images:
            text += tesserocr.image_to_text(img)
        return text


def generate_explanation_llm(text: str) -> str:
    prompt = f"""
You are a medical assistant. Summarize and explain the following medical document in simple terms for a patient to understand:

{text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(lambda: "demo-user-id")  # Replace with real auth
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB).")

    # Compress if image
    if file.content_type.startswith("image/"):
        compressed = compress_image(Image.open(io.BytesIO(contents)), max_size_mb=MAX_FILE_SIZE_MB)
        upload_bytes = compressed
    else:
        upload_bytes = contents

    # Upload to Supabase Storage
    file_ext = os.path.splitext(file.filename)[-1]
    storage_path = f"{user_id}/{file.filename}"
    res = supabase.storage().from_(BUCKET_NAME).upload(storage_path, upload_bytes, file.content_type)
    if not res.get("Key"):
        raise HTTPException(status_code=500, detail="Failed to upload file to storage.")
    file_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{storage_path}"

    # OCR extraction
    if file.content_type.startswith("image/"):
        extracted_text = extract_text_from_image(upload_bytes)
    elif file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(upload_bytes)
    else:
        extracted_text = ""

    # LLM explanation
    explanation = generate_explanation_llm(extracted_text)

    # Store in Supabase table
    data = {
        "user_id": user_id,
        "file_url": file_url,
        "file_type": file.content_type,
        "file_size": len(upload_bytes),
        "extracted_text": extracted_text,
        "explanation": explanation,
        "title": file.filename,
    }
    supabase.table("medical_documents").insert(data).execute()

    return JSONResponse({
        "file_url": file_url,
        "extracted_text": extracted_text,
        "explanation": explanation,
    })
