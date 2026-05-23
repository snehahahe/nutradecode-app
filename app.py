import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import plotly.graph_objects as go
import re

# 1. Set up the page
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="centered")

# --- PROFESSIONAL SIDEBAR & DIETARY PROFILES ---
with st.sidebar:
    st.title("🍃 NutraDecode")
    st.markdown("---")
    st.markdown("### 👤 Your Dietary Profile")
    st.write("Set your restrictions so our AI can warn you of harmful ingredients.")
    
    # User selects their dietary profile
    diet_prefs = st.multiselect(
        "Select all that apply:", 
        ["Vegan", "Vegetarian", "Keto", "Halal", "Kosher", "Nut Allergy", "Celiac / Gluten-Free", "Pregnant"]
    )
    
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This tool provides scientific analysis for informational purposes only. It does not constitute medical advice.")

# Configure Google Gemini
api_key = st.secrets.get("GEMINI_API_KEY")
model = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in available_models:
            model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            fallback_name = available_models[0].replace('models/', '')
            model = genai.GenerativeModel(fallback_name)
    except: pass

# Gauge Chart Function
def draw_nutrascore(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "<b>NutraScore</b><br><span style='font-size:0.8em;color:gray'>100 = Optimal Health | 0 = Highly Processed</span>"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "rgba(0,0,0,0)"}, # Hides the default bar
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 39], 'color': "#FF4B4B"},   # Red (F)
                {'range': [40, 69], 'color': "#FFA500"},  # Orange/Yellow (C)
                {'range': [70, 100], 'color': "#2E8B57"}  # Green (A)
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    return fig

# Header
st.title("🍃 NutraDecode")
st.markdown("**Your transparent, product label decoder.**")

st.markdown("### 🧠 Product Scanner")
category = st.radio("What are we scanning today?", ("🍎 Food Products / Snacks", "💊 Supplements / Medicine"))
upload_type = st.radio("How do you want to input the product?", ("📸 Upload an Image", "⌨️ Type the Product Name"))

user_image = None
product_name = ""

if upload_type == "📸 Upload an Image":
    uploaded_file = st.file_uploader("Upload a photo of the product front or label...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Uploaded Image", use_column_width=True)
else:
    product_name = st.text_input("Enter the exact product name (e.g., 'Doritos' or 'Advil'):")

# Format the dietary preferences to tell the AI
diet_string = ", ".join(diet_prefs) if diet_prefs else "None"

# The NEW Advanced Master Prompt
system_prompt = f"""
You are "NutraDecode," an elite Food Scientist and Pharmacist AI.
CRITICAL RULE: Identify the EXACT product ingredients using your knowledge base. Do not guess.

USER DIETARY PROFILE: {diet_string}. 
If ANY ingredient violates this profile, you MUST start your response with a massive red 🚨 WARNING section explaining exactly which ingredient violates their profile.

You must output a NUTRASCORE. Calculate this from 1 to 100. 
(100 = Whole, single-ingredient, perfectly healthy. 0 = Ultra-processed, artificial dyes, toxic additives).
Start your response exactly like this: "NUTRASCORE: [number]"

Format your response exactly like this:
NUTRASCORE: [number]

🚨 **Profile Alerts:** [Only include if it violates their selected diet]
🍎 **Product:** [Name]

🔬 **Exact Ingredient Breakdown:**
- **[Ingredient]:** [Why it is used, and if it is harmful]

⚠️ **Scientific Backing & PubMed Citations:**
- Identify the most controversial or harmful ingredient (e.g., Red 40, Titanium Dioxide).
- Provide a summary of its health effects.
- Provide a simulated link to a real PubMed or NIH study regarding this ingredient (e.g., "Study: Effects of [Ingredient] - pubmed.ncbi.nlm.nih.gov/search...").

🔄 **Healthy Alternative Recommender:**
- Suggest 3 healthier, less processed alternatives to this product that have higher NutraScores.
"""

if st.button("Decode ✨"):
    if not api_key:
        st.error("API Key missing! Please check your Streamlit secrets.")
    elif user_image is None and product_name == "":
        st.warning("Please upload an image or type a product name first!")
    else:
        with st.spinner("Analyzing profile, calculating NutraScore, and fetching scientific data..."):
            try:
                if user_image is not None:
                    response = model.generate_content([system_prompt, user_image])
                else:
                    response = model.generate_content(f"{system_prompt}\n\nProduct Name: {product_name}")
                
                result_text = response.text
                
                # Extract the NutraScore using Python logic
                score = 50 # Default
                match = re.search(r'NUTRASCORE:\s*(\d+)', result_text)
                if match:
                    score = int(match.group(1))
                    # Remove the "NUTRASCORE: 85" line from the text so it looks clean
                    result_text = re.sub(r'NUTRASCORE:\s*\d+\n?', '', result_text)
                
                # Display the Gauge Chart!
                st.plotly_chart(draw_nutrascore(score), use_container_width=True)
                
                # Display the rest of the analysis
                st.markdown(result_text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
