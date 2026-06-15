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
    .nav-container { display: flex; justify-content: space-between; align-items: center; padding: 25px 0; }
    .logo-text { font-size: 28px !important; font-weight: 800; color: #1A261D; letter-spacing: -0.5px; }
    .hero-title { font-size: 64px; font-weight: 800; color: #1A261D; line-height: 1.1; margin-top: 40px; }
    .hero-green { color: #43A047; }
    .card-green { background: #F1F8F1; border-radius: 32px; padding: 40px; border: 1px solid #E2EEE2; min-height: 380px; }
    .card-purple { background: #F9F5FF; border-radius: 32px; padding: 40px; border: 1px solid #EFE8FF; min-height: 380px; }
    .stats-bar { display: flex; justify-content: space-around; background: #F9FBF9; padding: 40px; border-radius: 24px; margin: 80px 0; border: 1px solid #F0F2F0; }
    .stButton>button { background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 25px !important; width: 100%; border: none !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# 3. CONFIGURE AI
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
    except: pass

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
st.markdown(f'<div class="nav-container"><div class="logo-text">🍃 NutraDecode</div></div>', unsafe_allow_html=True)

# 5. HERO
col_h1, col_h2 = st.columns([1.2, 1])
with col_h1:
    st.markdown('<div class="hero-title">Decode. Understand.<br><span class="hero-green">Choose Better.</span></div>', unsafe_allow_html=True)
with col_h2:
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

# 6. SCANNING SECTION
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="card-green"><h3>🔍 Quick Barcode Scan</h3></div>', unsafe_allow_html=True)
    st.write('<style>div.stTextInput {margin-top: -260px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    barcode = st.text_input("B", key="bar_input", label_visibility="collapsed", placeholder="Enter Barcode")
    if st.button("Scan Barcode"): pass

with c2:
    st.markdown('<div class="card-purple"><h3>🧠 Label Decoder</h3></div>', unsafe_allow_html=True)
    st.write('<style>div.stRadio {margin-top: -260px; padding: 0 40px;}</style>', unsafe_allow_html=True)
    mode = st.radio("M", ["📸 Photo Scan", "⌨️ Product Name"], horizontal=True, label_visibility="collapsed")
    
    up, p_name = None, ""
    
    # MODIFIED: Logic for both inputs in Photo Scan mode
    if mode == "📸 Photo Scan":
        up = st.file_uploader("U", type=['jpg','png'], label_visibility="collapsed")
        p_name = st.text_input("N_photo", placeholder="Step 2: Enter Product Name (Required)", label_visibility="collapsed")
    else:
        p_name = st.text_input("N_name", placeholder="Enter Product Name", label_visibility="collapsed")

    # 7. SYSTEM PROMPT
    diet = st.session_state.get('diet', 'None')
    system_prompt = f"""
    You are "NutraDecode," an elite Food Scientist and Pharmacist AI. Analyze for diet: {diet}.
    
    YOU MUST FOLLOW THIS EXACT ORDER AND HEADINGS:

    IF FOOD/DRINK/ICE CREAM:
    1. Start with 'NUTRASCORE: [0-100]'
    2. 🍎 **Product:** [Name]
    3. 🎯 **The Claim Check:** 
       - Claims Identified: [e.g. "Zero Sugar"]
       - The Scientific Truth: [e.g. "Uses Maltodextrin which spikes blood sugar"]
    4. ⚠️ **Who Should Avoid This:** 
       - [List specific medical conditions and WHY]
    5. ⚖️ **Serving Size & When to Consume**: [Serving context and frequency]
    6. 🔬 **Exact Ingredient Breakdown:** 
       - [Ingredient Name]: [Detailed explanation of its purpose and processing degree]

    --- DEEPER ANALYSIS ---
    7. **NutraDecode Expert Analysis**: (Classify processing via NOVA/Monteiro system and discuss long-term disease risks).
    8. **Nutritional Breakdown (per 100g)**: (Table including Energy, Carbs, Sugars, Fats, Protein, Sodium).
    9. **Nutra-Score Calculation (based on official algorithm)**: 
       - **Negative Points (A points)**: [Math for Energy, Saturated Fat, Sugars, Sodium]
       - **Positive Points (C points)**: [Math for Fibre, Protein, Fruits/Veg/Nuts]
       - **Final Logic**: [Show the Final Grade A-E calculation]
    10. **Citations**: [Mandatory PubMed references with PMID]

    IF SUPPLEMENT/MEDICINE:
    1. 💊 **Product:** [Name]
    2. **Primary Purpose**: [2 sentences]
    3. ⚠️ **Who Should Avoid This**
    4. 🔬 **What's Inside & Why (Active Ingredients)**
    5. ⏱️ **When & How to Consume**
    6. ⚖️ **Dosage**
    7. 🚫 **What NOT to take alongside this**
    8. **Citations**: [PubMed references with PMID]
    """

    if st.button("Decode with AI"):
        # Logic check: if in photo mode, both are required
        if mode == "📸 Photo Scan" and (not up or not p_name):
            st.warning("Please both upload a photo AND type the product name for a photo analysis.")
        elif mode == "⌨️ Product Name" and not p_name:
            st.warning("Please type a product name.")
        elif model:
            with st.spinner("Analyzing profile and generating report..."):
                try:
                    img = Image.open(up) if up else None
                    # We pass both the image and the name to the AI for max accuracy
                    if img and p_name:
                        response = model.generate_content([system_prompt, img, f"The product name is: {p_name}"])
                    elif img:
                        response = model.generate_content([system_prompt, img])
                    else:
                        response = model.generate_content(f"{system_prompt}\nProduct: {p_name}")
                    
                    text = response.text
                    score = 50
                    match = re.search(r'NUTRASCORE:\s*(\d+)', text)
                    if match: 
                        score = int(match.group(1))
                        text = re.sub(r'NUTRASCORE:\s*\d+\n?', '', text)
                    
                    st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                    st.markdown(text)
                except Exception as e: st.error(f"Error: {e}")

# 8. STATS BAR
st.markdown('<div class="stats-bar"><div style="text-align:center;"><span class="stat-val">100%</span><span class="stat-lab">Private</span></div><div style="text-align:center;"><span class="stat-val">AI</span><span class="stat-lab">Insights</span></div><div style="text-align:center;"><span class="stat-val">Thousands</span><span class="stat-lab">Decoded</span></div><div style="text-align:center;"><span class="stat-val">Better</span><span class="stat-lab">Choices</span></div></div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="logo-text">🍃 NutraDecode</div>', unsafe_allow_html=True)
    st.session_state['diet'] = st.multiselect("Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
