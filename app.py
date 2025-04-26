import streamlit as st
import os
import random
import uuid
from PIL import Image
from sentimental_model import generate_meme_caption, detect_sentiment, select_template_by_sentiment, add_caption_to_image

# Streamlit page configuration
st.set_page_config(page_title="Meme Generator", layout="wide", initial_sidebar_state="expanded")

# App header
st.title("Meme Generator with Gemini AI")
st.subheader("Generate a funny meme caption based on sentiment analysis")

# Styling for the layout and buttons
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #FF6347;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stTextArea>textarea {
        font-size: 18px;
        padding: 10px;
    }
    .stImage>img {
        border: 5px solid #FF6347;
    }
    </style>
    """, unsafe_allow_html=True
)

# Input prompt and sentiment selection in two columns
col1, col2 = st.columns([2, 1])
with col1:
    prompt = st.text_area("Enter your idea or sentence here", "New iPhone has no buttons")
with col2:
    sentiment_option = st.radio("Select the sentiment of the meme:", ('happy', 'sad', 'sarcastic'))

# Generate meme caption button
if st.button("Generate Meme Caption"):
    if prompt:
        sentiment, confidence = detect_sentiment(prompt)
        st.write(f"Detected sentiment: {sentiment.capitalize()} (Confidence: {confidence*100:.2f}%)")

        # Generate meme caption using Gemini
        meme_caption = generate_meme_caption(prompt, sentiment)
        st.write(f"Generated Caption: {meme_caption}")

        # Select template based on sentiment
        sentiment_folder = sentiment.lower()  # happy, sad, sarcastic
        templates = select_template_by_sentiment(sentiment_folder)

        if templates:
            # Select a template and generate meme
            template_image = random.choice(templates)
            img = Image.open(template_image)

            # Define the output file path for the meme
            output_path = os.path.join("outputs", f"meme_{uuid.uuid4().hex}.jpg")

            # Add caption to image and save
            add_caption_to_image(template_image, meme_caption, output_path)

            # Show the generated meme
            generated_meme = Image.open(output_path)
            st.image(generated_meme, caption="Generated Meme", use_container_width=True)

        else:
            st.warning("No templates available for the selected sentiment. Please check the templates folder.")


    else:
        st.error("Please enter a prompt to generate a meme caption.")
