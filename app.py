import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. PROFESSIONAL SVG ICONS (Crisp Vector Graphics)
svg_shield = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
svg_sparkle = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path></svg>'
svg_lock = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>'
svg_barcode = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2E4035" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14M21 5v14M7 5v14M17 5v14M12 5v14"></path></svg>'
svg_brain = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A5.5 5.5 0 0 0 4 7.5c0 1.63.71 3.1 1.83 4.12A4.01 4.01 0 0 0 4 15c0 2.2 1.8 4 4 4h.5c.34 3 2.84 5.5 5.5 5.5a5.5 5.5 0 0 0 5.5-5.5h.5c2.2 0 4-1.8 4-4 0-1.32-.65-2.5-1.65-3.23A5.5 5.5 0 0 0 14.5 2h-5z"></path></svg>'

# 3. ADVANCED STYLING
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap');
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 0rem; padding-bottom: 0rem; padding-left: 8%; padding-right: 8%;}}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #FFFFFF; }}

    /* Navbar */
    .nav-container {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }}
    .logo-img {{ height: 50px; }}
    .nav-links a {{ text-decoration: none; color: #4B5563; margin-left: 30px; font-size: 15px; font-weight: 600; }}
    .btn-get-started {{ background: #2E4035; color: white !important; padding: 10px 24px; border-radius: 10px; font-weight: 700; text-decoration: none; }}

    /* Hero */
    .hero-title {{ font-size: 64px; font-weight: 800; color: #1A261D; line-height: 1.1; margin-top: 40px; }}
    .hero-green {{ color: #43A047; }}
    .hero-subtitle {{ font-size: 18px; color: #6B7280; margin: 25px 0; max-width: 500px; line-height: 1.6; }}
    .feature-item {{ display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; color: #1A261D; }}
    .icon-circle {{ width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #F3F4F6; }}

    /* Cards */
    .card-green {{ background: #F1F8F1; border-radius: 32px; padding: 40px; border: 1px solid #E2EEE2; min-height: 380px; }}
    .card-purple {{ background: #F9F5FF; border-radius: 32px; padding: 40px; border: 1px solid #EFE8FF; min-height: 380px; }}
    .icon-bg {{ background: white; border-radius: 15px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }}
    
    /* Stats Bar */
    .stats-bar {{ display: flex; justify-content: space-around; background: #F9FBF9; padding: 40px; border-radius: 24px; margin: 80px 0; border: 1px solid #F0F2F0; }}
    .stat-val {{ font-size: 24px; font-weight: 800; color: #1A261D; display: block; }}
    .stat-lab {{ font-size: 13px; color: #6B7280; font-weight: 500; }}

    /* Buttons */
    .stButton>button {{ background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 25px !important; width: 100%; border: none !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; }}
</style>
""", unsafe_allow_html=True)

# 4. NAVBAR
st.markdown(f"""
<div class="nav-container">
    <img src="https://i.postimg.cc/k47P2PZk/57a7024e-b56e-41df-96e0-25298811f32a.png" class="logo-img">
    <div class="nav-links">
        <a href="#">How it works</a>
        <a href="#">About</a>
        <a href="#">Privacy</a>
        <a class="btn-get-started" href="#">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. HERO
col_hero1, col_hero2 = st.columns([1.2, 1])
with col_hero1:
    st.markdown("""
    <div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    """, unsafe_allow_html=True)
    
    # Feature list with SVG icons
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_shield}</div>Transparent</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_sparkle}</div>AI-Powered</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_lock}</div>Private</div>', unsafe_allow_html=True)

with col_hero2:
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

# 6. SCANNING SECTION
st.markdown('<div style="text-align:center; font-size:32px; font-weight:800; margin: 80px 0 40px 0;">Choose Your Scanning Option</div>', unsafe_allow_html=True)

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown(f"""
    <div class="card-green">
        <div class="icon-bg">{svg_barcode}</div>
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Quick Barcode Scan</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Instantly get insights by scanning a product barcode from the database.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stTextInput {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    barcode = st.text_input("Barcode Input", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")
    if st.button("Scan Barcode"):
        pass # Logic here

with col_card2:
    st.markdown(f"""
    <div class="card-purple">
        <div class="icon-bg">{svg_brain}</div>
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Label Decoder</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Upload a product label photo or enter the product name to decode with AI.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stRadio {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    mode = st.radio("Mode", ["📸 Photo", "⌨️ Name"], horizontal=True, label_visibility="collapsed")
    if mode == "📸 Photo":
        st.file_uploader("Upload", type=['jpg','png'], label_visibility="collapsed")
    else:
        st.text_input("Name", placeholder="Product Name", label_visibility="collapsed")
    if st.button("Decode with AI"):
        pass # Logic here

# 7. STATS FOOTER
st.markdown("""
<div class="stats-bar">
    <div class="stat-box" style="text-align:center;"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div class="stat-box" style="text-align:center;"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div class="stat-box" style="text-align:center;"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div class="stat-box" style="text-align:center;"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR (Dietary Profile)
with st.sidebar:
    st.image("https://i.postimg.cc/k47P2PZk/57a7024e-b56e-41df-96e0-25298811f32a.png", width=150)
    st.markdown("---")
    diet_prefs = st.multiselect("Your Dietary Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
