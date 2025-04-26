import os
import random
import uuid
from google import genai
from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont

# Initialize Google Gemini client
client = genai.Client(api_key="YOUR_API_KEY")  # Replace with your actual API key

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")


def detect_sentiment(text):
    result = sentiment_pipeline(text)[0]
    label = result["label"].lower()
    confidence = result["score"]

    # Simplify label mapping
    if "positive" in label:
        sentiment = "happy"
    elif "negative" in label:
        sentiment = "sad"
    else:
        sentiment = "sarcastic"

    return sentiment, confidence


def generate_meme_caption(prompt, sentiment):
    """Generate meme caption using Gemini, ensuring it mentions the main entity."""
    full_prompt = (
        f"Given the idea: '{prompt}', generate a SHORT, ONE-LINE humorous meme caption "
        f"that mentions the main subject (like 'iPhone' if present) explicitly. "
        f"The tone should be {sentiment}. Keep it funny and very short."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )
    return response.text.strip()


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
