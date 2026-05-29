import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. ASSET LINKS
# Replace 'snehahahe' with your actual GitHub username if different
logo_url = "https://raw.githubusercontent.com/snehahahe/nutradecode-official/main/logo.png"
hero_img_url = "https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png"

# 3. PROFESSIONAL SVG ICONS
svg_shield = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
svg_sparkle = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path></svg>'
svg_lock = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>'

# 4. ADVANCED DESIGNER CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 0rem; padding-bottom: 0rem; padding-left: 8%; padding-right: 8%;}}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #FFFFFF; }}

    /* Navbar */
    .nav-container {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }}
    .logo-img {{ height: 60px; width: auto; object-fit: contain; }}
    .nav-links a {{ text-decoration: none; color: #4B5563; margin-left: 30px; font-size: 15px; font-weight: 600; }}
    .btn-get-started {{ background: #2E4035; color: white !important; padding: 10px 24px; border-radius: 10px; font-weight: 700; text-decoration: none; }}

    /* Hero Section */
    .hero-title {{ font-size: 64px; font-weight: 800; color: #1A261D; line-height: 1.1; margin-top: 40px; }}
    .hero-green {{ color: #43A047; }}
    .hero-subtitle {{ font-size: 18px; color: #6B7280; margin: 25px 0; max-width: 500px; line-height: 1.6; }}
    .feature-item {{ display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; color: #1A261D; }}
    .icon-circle {{ width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #F3F4F6; }}

    /* Cards */
    .card-green {{ background: #F1F8F1; border-radius: 32px; padding: 40px; border: 1px solid #E2EEE2; min-height: 380px; }}
    .card-purple {{ background: #F9F5FF; border-radius: 32px; padding: 40px; border: 1px solid #EFE8FF; min-height: 380px; }}
    
    /* Stats Bar */
    .stats-bar {{ display: flex; justify-content: space-around; background: #F9FBF9; padding: 40px; border-radius: 24px; margin: 80px 0; border: 1px solid #F0F2F0; }}
    .stat-val {{ font-size: 24px; font-weight: 800; color: #1A261D; display: block; }}
    .stat-lab {{ font-size: 13px; color: #6B7280; font-weight: 500; }}

    /* Buttons */
    .stButton>button {{ background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 25px !important; width: 100%; border: none !important; font-weight: 700 !important; text-transform: uppercase; }}
</style>
""", unsafe_allow_html=True)

# 5. CONFIGURE AI BRAIN
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
    except: pass

# 6. HELPER FUNCTIONS
def draw_nutrascore(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "NutraScore", 'font': {'size': 24, 'color': "#2E4035"}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#2E4035"},
                 'steps': [{'range': [0, 40], 'color': "#FFCDD2"},
                           {'range': [40, 70], 'color': "#FFF9C4"},
                           {'range': [70, 100], 'color': "#C8E6C9"}]}))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def fetch_image_by_name(product_name):
    try:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={urllib.parse.quote(product_name)}&search_simple=1&action=process&json=1&page_size=1"
        res = requests.get(url, headers={"User-Agent": "NutraDecode/1.0"}).json()
        return res["products"][0].get("image_url", None) if res.get("products") else None
    except: return None

# 7. NAVIGATION BAR
st.markdown(f"""
<div class="nav-container">
    <img src="{logo_url}" class="logo-img">
    <div class="nav-links">
        <a href="#">How it works</a>
        <a href="#">About</a>
        <a href="#">Privacy</a>
        <a class="btn-get-started" href="#">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. HERO SECTION
col_h1, col_h2 = st.columns([1.2, 1])
with col_h1:
    st.markdown("""
    <div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_shield}</div>Transparent</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_sparkle}</div>AI-Powered</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="feature-item"><div class="icon-circle">{svg_lock}</div>Private</div>', unsafe_allow_html=True)

with col_h2:
    st.image(hero_img_url, use_column_width=True)

# 9. SCANNING SECTION
st.markdown('<div style="text-align:center; font-size:32px; font-weight:800; margin: 80px 0 40px 0;">Choose Your Scanning Option</div>', unsafe_allow_html=True)

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown("""
    <div class="card-green">
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Quick Barcode Scan</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Instantly get insights from our factual global database.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stTextInput {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    barcode = st.text_input("B-Input", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")
    if st.button("Scan Barcode"):
        if barcode:
            with st.spinner("Fetching..."):
                res = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json", headers={"User-Agent": "NutraDecode/1.0"}).json()
                if res.get("status") == 1:
                    p = res["product"]
                    st.success(f"Found: {p.get('product_name')}")
                    st.info(f"**Ingredients:** {p.get('ingredients_text', 'No data')}")
                else: st.error("Not found in database.")

with col_card2:
    st.markdown("""
    <div class="card-purple">
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Label Decoder</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Upload a label photo or type the product name to decode with AI.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stRadio {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    mode = st.radio("M", ["📸 Photo", "⌨️ Name"], horizontal=True, label_visibility="collapsed")
    
    user_image = None
    p_name = ""
    if mode == "📸 Photo":
        up = st.file_uploader("U", type=['jpg','png'], label_visibility="collapsed")
        if up: user_image = Image.open(up)
    else:
        p_name = st.text_input("N", placeholder="e.g. Organic Almond Milk", label_visibility="collapsed")

    if st.button("Decode with AI"):
        if model and (user_image or p_name):
            with st.spinner("Analyzing..."):
                try:
                    # Fetch web image if name provided
                    if p_name and not user_image:
                        img_url = fetch_image_by_name(p_name)
                        if img_url: st.image(img_url, width=200)
                    
                    # AI Analysis
                    diet = st.session_state.get('diet', 'None')
                    prompt = f"You are NutraDecode AI. Analyze ingredients for diet: {diet}. Give NUTRASCORE: [0-100]. Highlight harmful items with PubMed-style links."
                    response = model.generate_content([prompt, user_image]) if user_image else model.generate_content(f"{prompt}\nProduct: {p_name}")
                    
                    # Score Parsing & Gauge
                    score = 50
                    match = re.search(r'NUTRASCORE:\s*(\d+)', response.text)
                    if match: score = int(match.group(1))
                    
                    st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                    st.markdown(response.text)
                    st.caption("⚖️ AI Disclaimer: For informational use only. Verify with physical label.")
                except Exception as e: st.error(f"Error: {e}")

# 10. STATS FOOTER
st.markdown("""
<div class="stats-bar">
    <div style="text-align:center;"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div style="text-align:center;"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div style="text-align:center;"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div style="text-align:center;"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
""", unsafe_allow_html=True)

# 11. SIDEBAR
with st.sidebar:
    st.image(logo_url, width=150)
    st.markdown("---")
    st.session_state['diet'] = st.multiselect("Your Dietary Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
