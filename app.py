import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG (Hiding Streamlit default elements)
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. THE DESIGNER CSS (Matches your image exactly)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Hide Streamlit Header and Padding */
    header {visibility: hidden;}
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }

    /* Global Body */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAF8;
    }

    /* Navbar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        background-color: transparent;
    }
    .logo-text {
        font-size: 28px !important; /* Increased as requested */
        font-weight: 800;
        color: #1A261D;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-links {
        display: flex;
        gap: 30px;
        align-items: center;
    }
    .nav-links a {
        text-decoration: none;
        color: #4A4A4A;
        font-size: 15px;
        font-weight: 500;
    }
    .btn-get-started {
        background-color: #2E4035;
        color: white !important;
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: 600;
    }

    /* Hero Section */
    .hero-title {
        font-size: 64px;
        font-weight: 800;
        color: #1A261D;
        line-height: 1.1;
        margin-top: 40px;
    }
    .hero-green {
        color: #4CAF50;
    }
    .hero-subtitle {
        font-size: 18px;
        color: #5C6E5F;
        margin: 25px 0;
        max-width: 500px;
        line-height: 1.6;
    }
    .feature-list {
        display: flex;
        gap: 20px;
        margin-bottom: 40px;
    }
    .feature-item {
        font-size: 15px;
        font-weight: 600;
        color: #1A261D;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* Cards Section */
    .choose-title {
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #1A261D;
        margin: 60px 0 40px 0;
    }
    .custom-card {
        background: white;
        border-radius: 30px;
        padding: 40px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.02);
        border: 1px solid #F0F2F0;
        height: 100%;
    }
    .card-icon-container {
        width: 60px;
        height: 60px;
        background: #F1F8F1;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 22px;
        font-weight: 800;
        color: #1A261D;
        margin-bottom: 10px;
    }
    .card-desc {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 30px;
        line-height: 1.4;
    }

    /* Bottom Stats Bar */
    .stats-bar {
        display: flex;
        justify-content: space-around;
        background: #FFFFFF;
        padding: 40px;
        border-radius: 25px;
        margin: 60px 0;
        border: 1px solid #F0F2F0;
    }
    .stat-box { text-align: center; }
    .stat-val { font-size: 22px; font-weight: 800; color: #1A261D; display: block; }
    .stat-lab { font-size: 14px; color: #6B7280; }

    /* Hide Streamlit's red error boxes for custom styling */
    .stAlert { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. THE NAVIGATION BAR
st.markdown("""
<div class="nav-container">
    <div class="logo-text">🍃 NutraDecode</div>
    <div class="nav-links">
        <a href="#">How it works</a>
        <a href="#">About</a>
        <a href="#">Privacy</a>
        <a class="btn-get-started" href="#">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. THE HERO SECTION
col_hero1, col_hero2 = st.columns([1.2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    <div class="feature-list">
        <div class="feature-item">🛡️ Transparent</div>
        <div class="feature-item">✨ AI-Powered</div>
        <div class="feature-item">🔒 Private</div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    # This is where your Golden Halftone / Phone mockup image goes
    st.image("https://i.imgur.com/your_uploaded_image.png", use_column_width=True)

# 5. THE SCANNING CARDS
st.markdown('<div class="choose-title">Choose Your Scanning Option</div>', unsafe_allow_html=True)

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown("""
    <div class="custom-card">
        <div class="card-icon-container">🔍</div>
        <div class="card-title">Quick Barcode Scan</div>
        <div class="card-desc">Instantly get insights by scanning a product barcode from the database.</div>
    </div>
    """, unsafe_allow_html=True)
    # The actual functional input placed right below the card title
    barcode = st.text_input("Barcode", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")
    if st.button("Scan Barcode 🚀"):
        # Barcode Logic Here
        pass

with col_card2:
    st.markdown("""
    <div class="custom-card">
        <div class="card-icon-container">🧠</div>
        <div class="card-title">Label Decoder</div>
        <div class="card-desc">Upload a product label photo or enter the product name to decode with AI.</div>
    </div>
    """, unsafe_allow_html=True)
    # The actual functional inputs
    dec_mode = st.radio("Mode:", ["📸 Photo", "⌨️ Name"], horizontal=True, label_visibility="collapsed")
    if dec_mode == "📸 Photo":
        up_file = st.file_uploader("Upload", type=['jpg','png'], label_visibility="collapsed")
    else:
        p_name = st.text_input("Name", placeholder="e.g. Nutella", label_visibility="collapsed")
    
    if st.button("Decode with AI ✨"):
        # AI Logic Here
        pass

# 6. THE STATS FOOTER
st.markdown("""
<div class="stats-bar">
    <div class="stat-box"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div class="stat-box"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div class="stat-box"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div class="stat-box"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
<div style="text-align:center; padding-bottom: 50px;">
    <p style="color: #6B7280; font-size: 14px;">🛡️ We never store your images or personal data. Results are private and secure.</p>
</div>
""", unsafe_allow_html=True)
