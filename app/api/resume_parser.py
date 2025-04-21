import os
import io
import uuid
import json
import base64
import requests
from typing import Any, Dict, List

from fastapi import APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
from openai import OpenAI

# Load environment variables
load_dotenv()

# Router configuration
router = APIRouter(prefix="/resume", tags=["Resume"])

# Initialize OpenAI client
client = OpenAI()

# System prompt for resume parsing
SYSTEM_PROMPT = (
    "You are a resume parser. Extract the following fields from the images and return a JSON object with these keys:\n"
    "- name\n"
    "- location\n"
    "- tools/technologies\n"
    "- skillset\n"
    "- total years of experience\n"
    "- most-worked-on technology\n"
    "- certifications\n"
    "- education\n"
    "- projects\n"
    "- languages\n"
    "- contact info (email, phone)\n\n"
    "Only return a valid JSON object. Do NOT include explanations, notes, or markdown. Start and end with curly braces."
)


@router.post("/", response_model=Dict[str, Any])
async def upload_resume(file: UploadFile = File(...)):
    # Step 1: Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Step 2: Convert PDF to images
    try:
        pdf_bytes = await file.read()
        images = convert_from_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {e}")

    # Step 3: Prepare input for OpenAI
    content_list: List[Dict[str, Any]] = [{"type": "text", "text": SYSTEM_PROMPT}]
    for image in images:
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        content_list.append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        )

    # Step 4: Call OpenAI to extract structured data
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": content_list}],
            max_tokens=1500,
            temperature=0.2,
        )
        parsed = json.loads(resp.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI parsing failed: {e}")

    # —— New Step 5: Flatten certifications into strings —— #
    certs = parsed.get("certifications")
    if isinstance(certs, list) and certs and isinstance(certs[0], dict):
        parsed["certifications"] = [
            f"{c.get('name', '').strip()} — {c.get('issuer', '').strip()} ({c.get('date', '').strip()})"
            for c in certs
        ]

    # Step 6: Store result in Elasticsearch
    doc_id = str(uuid.uuid4())
    es_url = f"http://elasticsearch:9200/resumes/_doc/{doc_id}"
    headers = {"Content-Type": "application/json"}
    es_resp = requests.put(es_url, headers=headers, data=json.dumps(parsed))

    if es_resp.status_code not in (200, 201):
        raise HTTPException(status_code=es_resp.status_code, detail=es_resp.json())

    # Step 7: Return response
    return {"status": "inserted", "id": doc_id, "data": parsed}
