## 🧠 Instameme – Sentiment-Based Meme Generator

**Instameme** is a Streamlit-based web application that automatically generates memes from user-provided text. It combines sentiment analysis and AI-powered captioning to create personalized and humorous memes based on how your input *feels*.

### 🔧 Features
- 🔍 **Sentiment Detection** using a pre-trained RoBERTa model (`cardiffnlp/twitter-roberta-base-sentiment`) to classify input as *happy*, *sad*, or *sarcastic*
- 🤖 **Caption Generation** powered by **Gemini API** to produce creative and context-aware meme text
- 🖼️ **Meme Template Selection** based on the detected sentiment
- 🧾 **Dynamic Text Overlay** onto meme templates using PIL
- 💾 **Local Meme Storage** – generated memes are saved in the `outputs/` directory

### 🚀 How It Works
1. User enters a meme idea (e.g. “new iPhone has no buttons wow”)
2. Instameme detects the sentiment and displays confidence level
3. Gemini API generates a humorous caption based on the input and sentiment
4. A matching template is selected from `meme_templates/happy`, `sad`, or `sarcastic`
5. The caption is added to the image and displayed/downloaded as a final meme

