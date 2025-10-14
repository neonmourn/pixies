# main.py
import os
import io
import uuid
import base64
import random
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentimental_model import (
    generate_meme_caption,
    detect_sentiment,
    select_template_by_sentiment,
    add_caption_to_image,
)

# --- Setup ---
app = FastAPI(title="InstaMeme Backend")

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Serve the static frontend
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class GenerateRequest(BaseModel):
    prompt: str


@app.get("/", response_class=HTMLResponse)
async def root():
    # Serve the frontend index.html
    index_path = ROOT / "static" / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h3>Index not found. Put static/index.html in place.</h3>", status_code=500)
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")

    # 1) Detect sentiment
    sentiment, confidence = detect_sentiment(prompt)

    # 2) Pick template
    templates = select_template_by_sentiment(sentiment)
    if not templates:
        # gracefully return an informative message
        return JSONResponse({"error": f"No templates found for sentiment '{sentiment}'", "sentiment": sentiment}, status_code=200)

    # 3) Generate caption (may use Gemini if key present, otherwise local fallback)
    caption = generate_meme_caption(prompt, sentiment)

    # 4) Choose template and generate meme image file
    template_path = random.choice(templates)
    output_name = f"meme_{uuid.uuid4().hex}.jpg"
    output_path = OUTPUTS_DIR / output_name
    try:
        add_caption_to_image(template_path, caption, str(output_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create meme image: {e}")

    # 5) Return base64 image + metadata so frontend can render & provide download
    with open(output_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return {
        "image_b64": img_b64,
        "file_name": output_name,
        "caption": caption,
        "sentiment": sentiment,
        "confidence": round(confidence * 100, 2),
    }


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    p = OUTPUTS_DIR / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p, media_type="image/jpeg", filename=filename)
