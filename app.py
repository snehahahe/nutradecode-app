import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. DESIGNER CSS (Refined & Professional)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    header {visibility: hidden;}
    .main .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 8%; padding-right: 8%;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }

    /* Navbar */
    .nav-container { display: flex; justify-content: space-between; align-items: center; padding: 25px 0; }
    .logo-text { font-size: 28px !important; font-weight: 800; color: #1A261D; letter-spacing: -0.5px; }
    .nav-links a { text-decoration: none; color: #4B5563; margin-left: 30px; font-size: 15px; font-weight: 600; }
    .btn-get-started { background: #2E4035; color: white !important; padding: 10px 24px; border-radius: 10px; font-weight: 700; text-decoration: none; }

    /* Hero Section */
    .hero-title { font-size: 64px; font-weight: 800; color: #1A261D; line-height: 1.1; margin-top: 40px; }
    .hero-green { color: #43A047; }
    .hero-subtitle { font-size: 18px; color: #6B7280; margin: 25px 0; max-width: 500px; line-height: 1.6; }
    
    /* Feature List */
    .feature-item { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; color: #1A261D; }
    .icon-circle { 
        width: 40px; height: 40px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        background: #F3F4F6; font-size: 20px;
    }

    /* Cards */
    .card-green { background: #F1F8F1; border-radius: 32px; padding: 40px; border: 1px solid #E2EEE2; min-height: 380px; }
    .card-purple { background: #F9F5FF; border-radius: 32px; padding: 40px; border: 1px solid #EFE8FF; min-height: 380px; }
    .card-icon { background: white; border-radius: 15px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); font-size: 28px; }
    
    /* Stats Bar */
    .stats-bar { display: flex; justify-content: space-around; background: #F9FBF9; padding: 40px; border-radius: 24px; margin: 80px 0; border: 1px solid #F0F2F0; }
    .stat-val { font-size: 24px; font-weight: 800; color: #1A261D; display: block; }
    .stat-lab { font-size: 13px; color: #6B7280; font-weight: 500; }

    /* Buttons */
    .stButton>button { background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 25px !important; width: 100%; border: none !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# 3. AI BRAIN CONFIGURATION
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
    except: pass

# 4. HELPER FUNCTIONS
def draw_nutrascore(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "NutraScore", 'font': {'size': 24, 'color': "#2E4035"}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#2E4035"},
                 'steps': [{'range': [0, 40], 'color': "#FFCDD2"},
                           {'range': [40, 70], 'color': "#FFF9C4"},
                           {'range': [70, 100], 'color': "#C8E6C9"}]}))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# 5. NAVIGATION BAR
st.markdown(f"""
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

# 6. HERO SECTION
col_h1, col_h2 = st.columns([1.2, 1])
with col_h1:
    st.markdown("""
    <div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>
    <div class="hero-subtitle">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</div>
    """, unsafe_allow_html=True)
    
    # Simple, high-compatibility icons
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="feature-item"><div class="icon-circle">🛡️</div>Transparent</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="feature-item"><div class="icon-circle">✨</div>AI-Powered</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="feature-item"><div class="icon-circle">🔒</div>Private</div>', unsafe_allow_html=True)

with col_h2:
    # Keeps your custom phone/snack mockup link
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

# 7. SCANNING OPTIONS
st.markdown('<div style="text-align:center; font-size:32px; font-weight:800; margin: 80px 0 40px 0;">Choose Your Scanning Option</div>', unsafe_allow_html=True)

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown("""
    <div class="card-green">
        <div class="card-icon">🔍</div>
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Quick Barcode Scan</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Instantly get factual insights from our global database via barcode.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stTextInput {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    barcode = st.text_input("B-Input", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")
    if st.button("Scan Barcode"):
        if barcode:
            with st.spinner("Searching database..."):
                res = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json", headers={"User-Agent": "NutraDecode/1.0"}).json()
                if res.get("status") == 1:
                    p = res["product"]
                    st.success(f"Found: {p.get('product_name')}")
                    st.info(f"**Ingredients:** {p.get('ingredients_text', 'No data')}")
                else: st.error("Product not found. Try the Label Decoder!")

with col_card2:
    st.markdown("""
    <div class="card-purple">
        <div class="card-icon">🧠</div>
        <div style="font-size:24px; font-weight:800; color:#1A261D;">Label Decoder</div>
        <div style="color:#6B7280; font-size:14px; margin: 10px 0 30px 0;">Upload a label photo or type the product name for a deep AI analysis.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('<style>div.stRadio {margin-top: -140px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    mode = st.radio("M", ["📸 Photo Scan", "⌨️ Product Name"], horizontal=True, label_visibility="collapsed")
    
    user_image, p_name = None, ""
    if mode == "📸 Photo Scan":
        up = st.file_uploader("U", type=['jpg','png'], label_visibility="collapsed")
        if up: user_image = Image.open(up)
    else:
        p_name = st.text_input("N", placeholder="e.g. Organic Peanut Butter", label_visibility="collapsed")

    if st.button("Decode with AI ✨"):
        if model and (user_image or p_name):
            with st.spinner("Analyzing ingredients..."):
                try:
                    diet = st.session_state.get('diet', 'None')
                    prompt = f"NutraDecode Expert Analysis. Diet: {diet}. Give NUTRASCORE: [0-100]. Format scientifically with PubMed style citations."
                    response = model.generate_content([prompt, user_image]) if user_image else model.generate_content(f"{prompt}\nProduct: {p_name}")
                    
                    score = 50
                    match = re.search(r'NUTRASCORE:\s*(\d+)', response.text)
                    if match: score = int(match.group(1))
                    
                    st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                    st.markdown(response.text)
                except Exception as e: st.error(f"Error: {e}")

# 8. STATS BAR
st.markdown("""
<div class="stats-bar">
    <div style="text-align:center;"><span class="stat-val">100%</span><span class="stat-lab">Private & Secure</span></div>
    <div style="text-align:center;"><span class="stat-val">AI</span><span class="stat-lab">Powered Insights</span></div>
    <div style="text-align:center;"><span class="stat-val">Thousands</span><span class="stat-lab">Products Decoded</span></div>
    <div style="text-align:center;"><span class="stat-val">Better</span><span class="stat-lab">Health Choices</span></div>
</div>
""", unsafe_allow_html=True)

# 9. SIDEBAR (Fixed text logo)
with st.sidebar:
    st.markdown('<div class="logo-text">🍃 NutraDecode</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.session_state['diet'] = st.multiselect("Dietary Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
