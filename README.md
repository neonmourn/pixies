🧠 Instameme – Sentiment-Based Meme Generator
Instameme is a Streamlit-based web application that automatically generates memes from user-provided text. It combines sentiment analysis and AI-powered captioning to create personalized and humorous memes based on how your input feels.

🔧 Features:
🔍 Sentiment Detection using a pre-trained RoBERTa model (happy, sad, sarcastic)
🤖 Meme Caption Generation powered by Gemini API for witty and creative text
🖼️ Template Selection based on detected or user-selected sentiment
🧾 Dynamic Text Overlay onto meme templates using PIL
💾 Memes Saved Locally to the outputs/ directory

🚀 How It Works
-> User inputs a meme idea (e.g. “new iPhone has no buttons wow”)
-> Instameme detects sentiment of the input and allows manual override
-> Gemini API generates a caption tailored to the text and sentiment
-> Templates are fetched from happy/, sad/, or sarcastic/ folders
-> The caption is added to the image, and the final meme is displayed and saved
