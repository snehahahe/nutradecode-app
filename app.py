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
    .stButton>button { background: #2E4035 !important; color: white !important; border-radius: 12px !important; padding: 25px !important; width: 100%; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# 3. CONFIGURE AI (WITH TEMPERATURE 0.1 FOR MAXIMUM CONSISTENCY)
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        # We set temperature to 0.1 to make the AI factual and consistent
        generation_config = {
            "temperature": 0.1,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=generation_config
        )
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

# 5. SCANNING SECTION (Visuals only)
col_h1, col_h2 = st.columns([1.2, 1])
with col_h1:
    st.markdown('<div class="hero-title" style="font-size:64px; font-weight:800; color:#1A261D;">Decode. Understand.<br><span style="color:#43A047;">Choose Better.</span></div>', unsafe_allow_html=True)
with col_h2:
    st.image("https://i.postimg.cc/ZYX0xNdk/30419f86-e1cf-4781-8be1-fc0502830afb.png", use_column_width=True)

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    barcode = st.text_input("Barcode Search", placeholder="Enter Barcode")
with c2:
    mode = st.radio("Input Method", ["📸 Photo Scan", "⌨️ Product Name"], horizontal=True)
    up = st.file_uploader("Upload Label", type=['jpg','png'], label_visibility="collapsed") if mode == "📸 Photo Scan" else None
    p_name = st.text_input("N", placeholder="Enter Product Name", label_visibility="collapsed") if mode == "⌨️ Product Name" else ""

# 6. UPDATED FACT-BASED SYSTEM PROMPT
diet = st.session_state.get('diet', 'None')
system_prompt = f"""
You are "NutraDecode," a Clinical Food Scientist. 
CRITICAL MISSION: Use ONLY the visible text in the provided image. Do not use external brand knowledge if it contradicts the image.

STEP 1: TRANSCRIBE the Product Name and the FULL Ingredient list as seen in the image.
STEP 2: TRANSCRIBE the Nutrition Facts Table (Energy, Sugars, Sat Fat, Sodium, Protein, Fiber).

FOLLOW THIS EXACT RESPONSE FORMAT:

NUTRASCORE: [Calculated Number 0-100]

🍎 **Product Name (as seen on label):** [Name]

🎯 **The Claim Check:** 
- Claims Identified: [e.g. "High Protein"]
- The Scientific Truth: [e.g. "Product is actually 40% sugar, negating protein benefits"]

⚠️ **Who Should Avoid This:** 
- [Based on the transcribed ingredients and the user's diet: {diet}]

⚖️ **Serving Size & When to Consume:** [Specific context]

🔬 **Exact Ingredient Breakdown:** 
- [Ingredient]: [Purpose/Processing Level]

--- DEEPER ANALYSIS ---
**NutraDecode Expert Analysis**:
Classify via NOVA System. Explain long-term health risks of these specific transcribed ingredients.

**Nutritional Breakdown (per 100g)**:
[Table of values found in Step 2]

**Nutra-Score Calculation (Official Algorithm)**:
- **Negative Points (A points)**: Energy, Saturated Fat, Sugars, Sodium math.
- **Positive Points (C points)**: Fruits/Veg/Nuts, Fibre, Protein math.
- **Final Logic**: (A points - C points) mapped to Grade A-E.

**Citations**:
[PubMed references with PMID]
"""

if st.button("Decode with AI"):
    if model and (up or p_name):
        with st.spinner("Extracting label data and performing clinical analysis..."):
            try:
                img = Image.open(up) if up else None
                # Force the AI to be grounded in the image text
                response = model.generate_content([system_prompt, img]) if img else model.generate_content(f"{system_prompt}\nProduct: {p_name}")
                text = response.text
                
                score = 50
                match = re.search(r'NUTRASCORE:\s*(\d+)', text)
                if match: 
                    score = int(match.group(1))
                    text = re.sub(r'NUTRASCORE:\s*\d+\n?', '', text)
                
                st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                st.markdown(text)
            except Exception as e: st.error(f"Error: {e}")

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="logo-text">🍃 NutraDecode</div>', unsafe_allow_html=True)
    st.session_state['diet'] = st.multiselect("Dietary Profile:", ["Vegan", "Keto", "Halal", "Nut Allergy", "Pregnant"])
