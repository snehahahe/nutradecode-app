import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="wide")

# 2. DESIGNER CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    header {visibility: hidden;}
    .main .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 8%; padding-right: 8%;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    .logo-text { font-size: 28px !important; font-weight: 800; color: #1A261D; letter-spacing: -0.5px; }
    
    /* Section Title */
    .section-header {
        text-align: center;
        margin-top: 60px;
        margin-bottom: 40px;
    }
    .section-title { font-size: 32px; font-weight: 800; color: #1A261D; }
    .section-subtitle { font-size: 16px; color: #6B7280; }

    /* Button Styling */
    .stButton>button {
        background: #2E4035 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 20px 40px !important;
        width: 100%;
        font-weight: 700 !important;
        font-size: 18px !important;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. CONFIGURE AI (WITH AUTO-DETECT TO FIX 404 ERROR)
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        # Auto-detect available model names for this specific API key
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority: 1.5 Flash -> 1.5 Pro -> 1.0 Pro
        target_model = 'models/gemini-1.5-flash'
        if target_model not in available_models:
            target_model = 'models/gemini-1.5-pro' if 'models/gemini-1.5-pro' in available_models else available_models[0]
        
        model = genai.GenerativeModel(
            model_name=target_model,
            generation_config={"temperature": 0.1} # Keeping it factual
        )
    except Exception as e:
        st.error(f"AI Configuration Error: {e}")

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

# 4. NAVBAR
st.markdown(f'<div class="nav-container" style="padding: 20px 0;"><div class="logo-text">🍃 NutraDecode</div></div>', unsafe_allow_html=True)

# 5. HERO
col_h1, col_h2 = st.columns([1.2, 1])
with col_h1:
    st.markdown('<div style="font-size:64px; font-weight:800; color:#1A261D; line-height:1.1; margin-top:40px;">Decode. Understand.<br><span style="color:#43A047;">Choose Better.</span></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6B7280; font-size:18px; margin:20px 0;">NutraDecode helps you instantly decode product labels and make informed, healthier choices.</p>', unsafe_allow_html=True)
with col_h2:
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

# 6. SCANNING TOOLS SECTION
st.markdown("""
<div class="section-header">
    <div class="section-title">Choose Your Scanning Option</div>
    <div class="section-subtitle">Select a method below to begin your nutritional analysis</div>
</div>
""", unsafe_allow_html=True)

# Layout for the tools
tool_col1, tool_col2 = st.columns(2)

with tool_col1:
    st.markdown("### 🔍 Quick Barcode Scan")
    st.caption("Instantly get factual insights from our database.")
    barcode_input = st.text_input("Barcode", label_visibility="collapsed", placeholder="Enter Barcode (e.g. 049000000443)")

with tool_col2:
    st.markdown("### 🧠 Label Decoder")
    st.caption("Upload a label photo or type a name for AI analysis.")
    mode = st.radio("M", ["📸 Photo Scan", "⌨️ Product Name"], horizontal=True, label_visibility="collapsed")
    
    user_image, p_name = None, ""
    if mode == "📸 Photo Scan":
        up = st.file_uploader("U", type=['jpg','png'], label_visibility="collapsed")
        if up: user_image = Image.open(up)
    else:
        p_name = st.text_input("N", placeholder="Enter Product Name", label_visibility="collapsed")

# 7. ACTION BUTTON (Centered beneath both tools)
st.write("") # Spacing
button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
with button_col2:
    decode_clicked = st.button("Decode with AI ✨")

# 8. AI LOGIC
if decode_clicked:
    # Logic for Barcode First
    if barcode_input:
        with st.spinner("Fetching database records..."):
            res = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode_input}.json", headers={"User-Agent": "NutraDecode/1.0"}).json()
            if res.get("status") == 1:
                p = res["product"]
                st.success(f"Factual Data Found: {p.get('product_name')}")
                st.info(f"**Ingredients:** {p.get('ingredients_text', 'No data')}")
            else: st.error("Barcode not found in database. Please use the Photo Scan or Product Name options.")

    # Logic for AI Decoder
    elif user_image or p_name:
        if model:
            with st.spinner("Analyzing profile and performing clinical breakdown..."):
                try:
                    diet = st.session_state.get('diet', 'None')
                    # Using your requested detailed prompt format
                    system_prompt = f"""You are NutraDecode AI. Analyze for diet: {diet}. 
                    If Food: Give NUTRASCORE: [0-100], Claim Check, Warning, Serving Size, Ingredient Breakdown, Nutri-Score math, and PubMed PMID citations.
                    If Supplement: Give Name, Purpose, Active Ingredients, Warnings, Dosage, and Interactions."""
                    
                    response = model.generate_content([system_prompt, user_image]) if user_image else model.generate_content(f"{system_prompt}\nProduct: {p_name}")
                    text = response.text
                    
                    # Extract score for gauge
                    score = 50
                    match = re.search(r'NUTRASCORE:\s*(\d+)', text)
                    if match: 
                        score = int(match.group(1))
                        text = re.sub(r'NUTRASCORE:\s*\d+\n?', '', text)
                    
                    st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                    st.markdown(text)
                except Exception as e: st.error(f"An error occurred: {e}")
        else:
            st.error("AI Model not available. Check your API key.")
    else:
        st.warning("Please provide a Barcode, Photo, or Product Name first!")

# 9. STATS BAR
st.markdown('<div style="display:flex; justify-content:space-around; background:#F9FBF9; padding:40px; border-radius:24px; margin-top:60px; border:1px solid #F0F2F0;"><div style="text-align:center;"><span style="font-weight:800;">100%</span><br><small>Private</small></div><div style="text-align:center;"><span style="font-weight:800;">AI</span><br><small>Insights</small></div><div style="text-align:center;"><span style="font-weight:800;">Thousands</span><br><small>Decoded</small></div><div style="text-align:center;"><span style="font-weight:800;">Better</span><br><small>Choices</small></div></div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="logo-text">🍃 NutraDecode</div>', unsafe_allow_html=True)
    st.session_state['diet'] = st.multiselect("Dietary Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
