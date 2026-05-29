import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. ADVANCED CSS INJECTION (The "Designer" Layer)
st.markdown("""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Playfair+Display:wght@700&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, #F8FAF8 0%, #FFFFFF 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Navbar Styling */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 5%;
        background: white;
        border-bottom: 1px solid #EAEAEA;
    }
    .nav-links a {
        text-decoration: none;
        color: #4A4A4A;
        margin: 0 15px;
        font-size: 14px;
    }
    .get-started-btn {
        background-color: #2E4035;
        color: white !important;
        padding: 8px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
    }

    /* Hero Section */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 55px;
        color: #1A261D;
        line-height: 1.1;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        color: #556B2F;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .feature-tag {
        display: inline-flex;
        align-items: center;
        margin-right: 20px;
        font-size: 14px;
        color: #2E4035;
    }

    /* Scanning Cards */
    .section-title {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #1A261D;
        margin-top: 50px;
        margin-bottom: 30px;
    }
    .custom-card {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        border: 1px solid #F0F2F0;
        min-height: 350px;
    }
    
    /* Stats Bar */
    .stats-container {
        display: flex;
        justify-content: space-around;
        padding: 40px 0;
        background: #F9FBF9;
        border-radius: 20px;
        margin-top: 60px;
    }
    .stat-item {
        text-align: center;
    }
    .stat-number {
        font-weight: bold;
        font-size: 20px;
        color: #1A261D;
        display: block;
    }
    .stat-label {
        font-size: 13px;
        color: #6B7280;
    }

    /* Input & Button Styling */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        padding: 12px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E4035 !important;
        color: white !important;
        border-radius: 12px;
        padding: 12px;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# 3. TOP NAVIGATION
st.markdown("""
<div class="nav-container">
    <div style="font-size: 22px; font-weight: bold; color: #2E4035;">🍃 NutraDecode</div>
    <div class="nav-links">
        <a href="#">How it works</a>
        <a href="#">About</a>
        <a href="#">Privacy</a>
        <a class="get-started-btn" href="#">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. HERO SECTION
st.write("") # Spacing
hero_col1, hero_col2 = st.columns([1.2, 1])

with hero_col1:
    st.write("")
    st.markdown('<h1 class="hero-title">Decode. Understand.<br><span style="color: #4CAF50;">Choose Better.</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</p>', unsafe_allow_html=True)
    
    # Feature icons
    st.markdown("""
    <div style="display: flex;">
        <div class="feature-tag">🛡️ <b>Transparent</b></div>
        <div class="feature-tag">✨ <b>AI-Powered</b></div>
        <div class="feature-tag">🔒 <b>Private</b></div>
    </div>
    """, unsafe_allow_html=True)

with hero_col2:
    # This simulates the "Phone Mockup" side of your image
    st.image("https://img.freepik.com/free-photo/healthy-food-background_23-2148119103.jpg", use_column_width=True)

# 5. SCANNING OPTIONS
st.markdown('<div class="section-title">Choose Your Scanning Option</div>', unsafe_allow_html=True)

card_col1, card_col2 = st.columns(2)

with card_col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Quick Barcode Scan")
    st.caption("Instantly get insights by scanning a product barcode.")
    barcode = st.text_input("Enter Barcode", placeholder="049000000443", label_visibility="collapsed")
    if st.button("Scan Barcode"):
        # (Logics for barcode remain the same as before)
        pass
    st.markdown('</div>', unsafe_allow_html=True)

with card_col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Label Decoder")
    st.caption("Upload a product label or enter the product name to decode.")
    
    # Selection for decoder
    decoder_mode = st.selectbox("Method:", ["Upload Image", "Enter Name"])
    
    if decoder_mode == "Upload Image":
        uploaded_file = st.file_uploader("Upload...", type=["jpg", "png"], label_visibility="collapsed")
    else:
        product_name = st.text_input("Enter Name", placeholder="e.g. Nutella", label_visibility="collapsed")
        
    if st.button("Decode with AI ✨"):
        # (AI Logic remains the same as before)
        pass
    st.markdown('</div>', unsafe_allow_html=True)

# 6. STATS FOOTER
st.markdown("""
<div class="stats-container">
    <div class="stat-item">
        <span class="stat-number">100%</span>
        <span class="stat-label">Private & Secure</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">AI</span>
        <span class="stat-label">Powered Insights</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">Thousands</span>
        <span class="stat-label">Products Decoded</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">Better</span>
        <span class="stat-label">Health Choices</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar (Keep your dietary profile settings here)
with st.sidebar:
    st.title("👤 Profile")
    diet_prefs = st.multiselect("Restrictions:", ["Vegan", "Keto", "Nut Allergy", "Pregnant"])
