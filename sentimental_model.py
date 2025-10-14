# # sentimental_model.py
# import os
# import random
# from pathlib import Path
# import re
# import google.generativeai as genai
# from transformers import pipeline
# from PIL import Image, ImageDraw, ImageFont

# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# if GOOGLE_API_KEY:
#     genai.configure(api_key=GOOGLE_API_KEY)

# # load sentiment model if available
# try:
#     sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# except Exception as e:
#     sentiment_pipeline = None
#     print(f"[warn] sentiment pipeline load failed: {e}. Using heuristic fallback.")


# def detect_sentiment(text: str):
#     """
#     Detect sentiment using Hugging Face 'cardiffnlp/twitter-roberta-base-sentiment' model.
#     Returns ('happy' | 'sad' | 'sarcastic', confidence).
#     """

#     if not text or text.strip() == "":
#         return "sarcastic", 0.0

#     if sentiment_pipeline is not None:
#         try:
#             # CardiffNLP returns LABEL_0 (negative), LABEL_1 (neutral), LABEL_2 (positive)
#             result = sentiment_pipeline(text)[0]
#             label = result.get("label", "").upper()
#             confidence = float(result.get("score", 0.0))

#             if label in ["LABEL_2", "POSITIVE"]:
#                 return "happy", confidence
#             elif label in ["LABEL_0", "NEGATIVE"]:
#                 return "sad", confidence
#             elif label in ["LABEL_1", "NEUTRAL"]:
#                 return "sarcastic", confidence
#             else:
#                 return "sarcastic", confidence

#         except Exception as e:
#             print(f"[warn] Sentiment model error: {e}. Using fallback rules.")

#     # --- Simple fallback if model not available ---
#     lower = text.lower()
#     positive_words = ["love", "great", "awesome", "good", "win", "yay", "best", "success"]
#     negative_words = ["hate", "bad", "broken", "fail", "worst", "sad", "angry", "tired"]

#     pos = any(w in lower for w in positive_words)
#     neg = any(w in lower for w in negative_words)

#     if pos and not neg:
#         return "happy", 0.7
#     if neg and not pos:
#         return "sad", 0.7
#     return "sarcastic", 0.5


# def generate_meme_caption(prompt, sentiment):
#     """Generate meme caption using Gemini, ensuring it mentions the main entity."""
#     full_prompt = (
#         f"Given the idea: '{prompt}', generate a SHORT, ONE-LINE humorous meme caption "
#         f"that mentions the main subject (like 'iPhone' if present) explicitly. "
#         f"The tone should be {sentiment}. Keep it funny and very short."
#     )
#     response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=full_prompt,
#     )
#     return response.text.strip()



# def select_template_by_sentiment(sentiment_folder: str, root_folder: str = "templates"):
#     folder_path = Path(root_folder) / sentiment_folder
#     if not folder_path.exists():
#         return []
#     files = [str(p) for p in sorted(folder_path.iterdir()) if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
#     return files


# def add_caption_to_image(template_path: str, caption: str, output_path: str):
#     image = Image.open(template_path).convert("RGBA")
#     draw = ImageDraw.Draw(image)
#     font_path_candidates = [
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
#         "/usr/share/fonts/truetype/arial.ttf",
#         "arial.ttf",
#         "DejaVuSans-Bold.ttf",
#     ]
#     font = None
#     for fp in font_path_candidates:
#         try:
#             font = ImageFont.truetype(fp, size=36)
#             break
#         except Exception:
#             font = None
#     if font is None:
#         font = ImageFont.load_default()

#     caption = " ".join(caption.splitlines())[:180]
#     max_width = int(image.width * 0.92)
#     font_size = 56
#     while font_size > 14:
#         try:
#             if isinstance(font, ImageFont.FreeTypeFont):
#                 try:
#                     font_candidate = ImageFont.truetype(font.path, font_size)
#                 except Exception:
#                     font_candidate = ImageFont.truetype(font_path_candidates[0], font_size) if Path(font_path_candidates[0]).exists() else font
#             else:
#                 font_candidate = font
#         except Exception:
#             font_candidate = font
#         bbox = draw.textbbox((0, 0), caption, font=font_candidate)
#         text_w = bbox[2] - bbox[0]
#         if text_w <= max_width or font_size <= 18:
#             font = font_candidate
#             break
#         font_size -= 2

#     bbox = draw.textbbox((0, 0), caption, font=font)
#     text_w = bbox[2] - bbox[0]
#     text_h = bbox[3] - bbox[1]
#     x = (image.width - text_w) // 2
#     y = image.height - text_h - int(image.height * 0.04)

#     outline_range = max(1, int(font_size / 15))
#     for ox in range(-outline_range, outline_range + 1):
#         for oy in range(-outline_range, outline_range + 1):
#             draw.text((x + ox, y + oy), caption, font=font, fill=(0, 0, 0, 255))

#     draw.text((x, y), caption, font=font, fill=(255, 255, 255, 255))

#     out = Image.new("RGB", image.size, (255, 255, 255))
#     out.paste(image, mask=image.split()[3])
#     out.save(output_path, format="JPEG", quality=90)
import os
import random
import uuid
import google.generativeai as genai

from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont

# Initialize Google Gemini client
genai.configure(api_key="YOUR_API_KEY")  # Replace with your actual API key

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")


def detect_sentiment(text):
    if not text or text.strip() == "":
        return "sarcastic", 0.0

    # Model prediction
    result = sentiment_pipeline(text)[0]
    label = result["label"].lower()
    confidence = result["score"]

    # Heuristic keywords
    text_lower = text.lower()
    positive_words = ["yay", "hooray", "won", "awesome", "great", "success"]
    negative_words = ["fail", "sad", "angry", "bad", "worst"]

    # Keyword override
    if any(w in text_lower for w in positive_words):
        return "happy", 0.9
    elif any(w in text_lower for w in negative_words):
        return "sad", 0.9

    # Use model otherwise
    if "positive" in label:
        sentiment = "happy"
    elif "negative" in label:
        sentiment = "sad"
    else:
        sentiment = "sarcastic"

    return sentiment, confidence


def generate_meme_caption(prompt: str, sentiment: str) -> str:
    """
    Generate a meme-style caption using Gemini API.
    Uses the same prompt structure and API call as Code B.
    """
    prompt = (prompt or "").strip()
    if not prompt:
        return "When words fail... memes speak."

    full_prompt = (
        f"Given the idea: '{prompt}', generate a SHORT, ONE-LINE humorous meme caption "
        f"that mentions the main subject (like 'iPhone' if present) explicitly. "
        f"The tone should be {sentiment}. Keep it funny and very short."
    )

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(full_prompt)
        text = (response.text or "").strip()
        if text:
            return text.splitlines()[0].strip("“”\"'•- ")
    except Exception as e:
        print(f"[warn] Gemini generation failed: {e}")

    # Fallback in case Gemini fails
    return "When words fail... memes speak."





def select_template_by_sentiment(sentiment_folder):
    folder_path = os.path.join("templates", sentiment_folder)
    if not os.path.exists(folder_path):
        return []
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
            f.lower().endswith((".png", ".jpg", ".jpeg"))]


def add_caption_to_image(template_path, caption, output_path):
    # Open the image
    image = Image.open(template_path).convert("RGBA")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Use the default font if the custom font isn't available
    try:
        font = ImageFont.truetype("arial.ttf", 28)  # Try custom font
    except IOError:
        font = ImageFont.load_default()  # Use default font if custom font is missing

    # Use textbbox to calculate text size
    bbox = draw.textbbox((0, 0), caption, font=font)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]  # Get width and height from bbox

    # Position the caption
    text_position = ((image.width - width) // 2, image.height - height - 10)

    # Add the caption text
    draw.text(text_position, caption, font=font, fill="white")

    # Convert the image to RGB before saving as JPEG
    image_rgb = image.convert("RGB")

    # Save the new image as JPEG
    image_rgb.save(output_path, "JPEG")