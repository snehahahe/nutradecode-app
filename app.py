import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. PROFESSIONAL SVG ICONS (Replacing Emojis)
# These are the crisp, professional icons from your mockup
icon_shield = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
icon_ai = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>'
icon_private = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
icon_barcode = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14M21 5v14M7 5v14M17 5v14M12 5v14"></path></svg>'
icon_brain = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A5.5 5.5 0 0 0 4 7.5c0 1.63.71 3.1 1.83 4.12A4.01 4.01 0 0 0 4 15c0 2.2 1.8 4 4 4h.5c.34 3 2.84 5.5 5.5 5.5a5.5 5.5 0 0 0 5.5-5.5h.5c2.2 0 4-1.8 4-4 0-1.32-.65-2.5-1.65-3.23A5.5 5.5 0 0 0 14.5 2h-5z"></path></svg>'

# 3. ADVANCED DESIGNER CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    header {{visibility: hidden;}}
    .main .block-container {{
        padding-top: 0rem;
        padding-left: 8%;
        padding-right: 8%;
    }}

    .logo-text {{
        font-size: 32px !important;
        font-weight: 800;
        color: #1A261D;
        letter-spacing: -1px;
    }}

    .hero-title {{
        font-size: 72px;
        font-weight: 800;
        color: #1A261D;
        line-height: 1.05;
        margin-top: 60px;
    }}
    .hero-green {{ color: #4CAF50; }}
    
    .hero-subtitle {{
        font-size: 20px;
        color: #5C6E5F;
        margin: 30px 0;
        max-width: 550px;
        line-height: 1.6;
    }}

    .feature-list {{ display: flex; gap: 40px; margin-bottom: 50px; }}
    .feature-item {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 16px;
        font-weight: 600;
        color: #1A261D;
    }}

    .custom-card {{
        background: white;
        border-radius: 32px;
        padding: 50px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.03);
        border: 1px solid #F0F2F0;
        transition: 0.3s;
    }}
    .icon-box {{
        width: 70px;
        height: 70px;
        background: #F1F8F1;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 25px;
    }}

    /* Stats bar styling */
    .stats-bar {{
        display: flex;
        justify-content: space-around;
        background: #FFFFFF;
        padding: 50px;
        border-radius: 30px;
        margin: 80px 0;
        border: 1px solid #F0F2F0;
    }}
    .stat-val {{ font-size: 24px; font-weight: 800; color: #1A261D; display: block; }}
    .stat-lab {{ font-size: 14px; color: #6B7280; font-weight: 500; }}

    /* Button Styling */
    .stButton>button {{
        background-color: #2E4035 !important;
        border-radius: 12px;
        padding: 25px !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
</style>
""", unsafe_allow_html=True)

# 4. NAVBAR
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 30px 0;">
    <div class="logo-text">NutraDecode</div>
    <div style="display: flex; gap: 40px; align-items: center;">
        <a style="text-decoration:none; color:#4A4A4A; font-weight:600;" href="#">How it works</a>
        <a style="text-decoration:none; color:#4A4A4A; font-weight:600;" href="#">About</a>
        <a style="text-decoration:none; color:#4A4A4A; font-weight:600;" href="#">Privacy</a>
        <div style="background:#2E4035; color:white; padding:12px 28px; border-radius:12px; font-weight:700; cursor:pointer;">Get Started</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. HERO SECTION
col_h1, col_h2 = st.columns([1.3, 1])

with col_h1:
    st.markdown(f"""
    <div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    <div class="feature-list">
        <div class="feature-item">{icon_shield} Transparent</div>
        <div class="feature-item">{icon_ai} AI-Powered</div>
        <div class="feature-item">{icon_private} Private</div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    # High-quality aesthetic product image
    st.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=1000", use_column_width=True)

# 6. SCANNING SECTION
st.markdown('<div style="text-align:center; font-size:32px; font-weight:800; margin: 80px 0 50px 0;">Choose Your Scanning Option</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-box">{icon_barcode}</div>
        <div style="font-size:24px; font-weight:800; margin-bottom:10px;">Quick Barcode Scan</div>
        <div style="color:#6B7280; margin-bottom:30px;">Instantly get insights by scanning a product barcode from our database.</div>
    </div>
    """, unsafe_allow_html=True)
    barcode = st.text_input("Barcode Input", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")
    if st.button("Scan Barcode"):
        pass # Barcode logic

with c2:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-box">{icon_brain}</div>
        <div style="font-size:24px; font-weight:800; margin-bottom:10px;">Label Decoder</div>
        <div style="color:#6B7280; margin-bottom:30px;">Upload a product label photo or enter the product name to decode.</div>
    </div>
    """, unsafe_allow_html=True)
    mode = st.radio("Input Method", ["Upload Image", "Product Name"], horizontal=True, label_visibility="collapsed")
    if mode == "Upload Image":
        st.file_uploader("Upload", type=['jpg','png'], label_visibility="collapsed")
    else:
        st.text_input("Name", placeholder="e.g. Organic Almond Milk", label_visibility="collapsed")
    if st.button("Start Analysis"):
        pass # AI Logic

# 7. STATS BAR
st.markdown("""
<div class="stats-bar">
    <div class="stat-box"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div class="stat-box"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div class="stat-box"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div class="stat-box"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
""", unsafe_allow_html=True)
