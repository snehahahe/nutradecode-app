# 🍃 NutraDecode
**Your transparent, AI-powered product label decoder.**

NutraDecode is a web application designed to bring radical transparency to consumer products by analyzing barcodes, product names, and images to decode complex food and supplement ingredients.

## 🚀 Live Demo
[Click here to use NutraDecode Live](https://nutradecode.streamlit.app)

## 🛠️ Features
- **Factual Database Pulling:** Uses the Open Food Facts API to pull real-world product ingredients via barcode, eliminating AI hallucinations.
- **AI Label Decoder:** Utilizes Google Gemini's Vision AI to perform OCR and nutritional analysis on user-uploaded images of product labels.
- **Scientific Claim Checking:** Cross-references marketing claims (e.g., "Zero Sugar") against actual ingredient profiles.
- **Health Warnings:** Flags chemical additives, highly processed ingredients, and specific medical contraindications (e.g., Diabetics, pregnant women).

## 💻 Tech Stack
- **Frontend/Backend:** Python, Streamlit
- **APIs:** Open Food Facts REST API
- **AI/LLM:** Google Generative AI (Gemini 1.5 Flash Vision)
