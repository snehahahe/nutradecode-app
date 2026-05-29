import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. THE EXACT CSS DESIGN
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap');

    /* Hide Streamlit elements */
    header {visibility: hidden;}
    .main .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 6%; padding-right: 6%;}

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
    }

    /* Navbar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px 0;
    }
    .logo { font-size: 26px; font-weight: 800; color: #1A261D; display: flex; align-items: center; gap: 10px; }
    .nav-links a { text-decoration: none; color: #4B5563; margin-left: 30px; font-size: 15px; font-weight: 500; }
    .btn-get-started { background: #2E4035; color: white !important; padding: 10px 24px; border-radius: 12px; font-weight: 700; text-decoration: none; }

    /* Hero Section */
    .hero-title { font-size: 68px; font-weight: 800; color: #1A261D; line-height: 1.1; margin-top: 50px; }
    .hero-highlight { color: #43A047; }
    .hero-subtitle { font-size: 18px; color: #6B7280; margin: 25px 0 40px 0; max-width: 500px; line-height: 1.6; }
    
    .feature-row { display: flex; gap: 30px; margin-bottom: 40px; }
    .feature-item { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 700; color: #1A261D; }
    .icon-circle { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #F3F4F6; }

    /* Cards Layout */
    .section-header { text-align: center; font-size: 28px; font-weight: 800; color: #1A261D; margin: 80px 0 40px 0; }
    
    /* Green Card (Left) */
    .card-green { background: #F1F8F1; border-radius: 32px; padding: 40px; border: 1px solid #E2EEE2; min-height: 380px; }
    .icon-green { background: white; border-radius: 20px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }

    /* Purple Card (Right) */
    .card-purple { background: #F9F5FF; border-radius: 32px; padding: 40px; border: 1px solid #EFE8FF; min-height: 380px; }
    .icon-purple { background: white; border-radius: 20px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }

    .card-title { font-size: 22px; font-weight: 800; color: #1A261D; margin-bottom: 8px; }
    .card-text { font-size: 14px; color: #6B7280; line-height: 1.5; margin-bottom: 30px; }

    /* Stats Bar */
    .stats-bar { display: flex; justify-content: space-around; background: #F9FBF9; padding: 40px; border-radius: 24px; margin: 80px 0; }
    .stat-item { text-align: center; padding: 0 40px; border-right: 1px solid #E5E7EB; }
    .stat-item:last-child { border-right: none; }
    .stat-val { font-size: 24px; font-weight: 800; color: #1A261D; display: block; }
    .stat-lab { font-size: 13px; color: #6B7280; font-weight: 500; }

    /* Custom Streamlit Input Styling */
    .stTextInput>div>div>input { border-radius: 12px !important; padding: 12px !important; border: 1px solid #D1D5DB !important; }
    .stButton>button { background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 12px 24px !important; width: 100%; border: none !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# 3. NAVBAR
st.markdown("""
<div class="nav-container">
    <div class="logo">🍃 NutraDecode</div>
    <div class="nav-links">
        <a href="#">How it works</a>
        <a href="#">About</a>
        <a href="#">Privacy</a>
        <a class="btn-get-started" href="#">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. HERO SECTION
col_hero1, col_hero2 = st.columns([1.2, 1])

with col_hero1:
    st.markdown("""
    <div class="hero-title">Decode. Understand.<br><span class="hero-highlight">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    <div class="feature-row">
        <div class="feature-item"><div class="icon-circle">🛡️</div><div><b>Transparent</b><br><span style="font-weight:400; color:#6B7280; font-size:12px;">See what's inside</span></div></div>
        <div class="feature-item"><div class="icon-circle">✨</div><div><b>AI-Powered</b><br><span style="font-weight:400; color:#6B7280; font-size:12px;">Smart insights</span></div></div>
        <div class="feature-item"><div class="icon-circle">🔒</div><div><b>Private</b><br><span style="font-weight:400; color:#6B7280; font-size:12px;">Your data stays yours</span></div></div>
    </div>
    """, unsafe_allow_html=True)

with col_hero2:
    # REPLACE THIS LINK with your uploaded almond packaging mockup
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

# 5. SCANNING SECTION
st.markdown('<div class="section-header">Choose Your Scanning Option</div>', unsafe_allow_html=True)

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown("""
    <div class="card-green">
        <div class="icon-green">🔳</div>
        <div class="card-title">Quick Barcode Scan</div>
        <div class="card-text">Instantly get insights by scanning a product barcode from the global database.</div>
    </div>
    """, unsafe_allow_html=True)
    # Positioning input over the card visually
    st.write('<style>div.stTextInput {margin-top: -150px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    barcode = st.text_input("Barcode Search", label_visibility="collapsed", placeholder="Enter Product Barcode (e.g. 049000000443)")
    st.write('<style>div.stButton {padding: 0 40px; margin-bottom: 50px;}</style>', unsafe_allow_html=True)
    if st.button("Scan Barcode"):
        pass

with col_card2:
    st.markdown("""
    <div class="card-purple">
        <div class="icon-purple">🧠</div>
        <div class="card-title">Label Decoder</div>
        <div class="card-text">Upload a product label photo or enter the product name to decode with AI.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stRadio {margin-top: -150px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    mode = st.radio("Mode", ["Upload Image", "Enter Name"], horizontal=True, label_visibility="collapsed")
    if mode == "Upload Image":
        st.file_uploader("Upload", type=['jpg','png'], label_visibility="collapsed")
    else:
        st.text_input("Name", placeholder="Product Name", label_visibility="collapsed")
    if st.button("Start Analysis ✨"):
        pass

# 6. STATS BAR
st.markdown("""
<div style="text-align:center; color:#6B7280; font-size:13px; margin-top:100px;">🛡️ We never store your images or personal data. Results are private and secure.</div>
<div class="stats-bar">
    <div class="stat-item"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div class="stat-item"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div class="stat-item"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div class="stat-item"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
""", unsafe_allow_html=True)
