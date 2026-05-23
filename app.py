import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image

# 1. Set up the page
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="centered")

# Configure Google Gemini (Using the 'latest' model version)
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Header
st.title("🍃 NutraDecode")
st.markdown("**Your transparent, product label decoder.**")

# ==========================================
# TOOL 1: THE BARCODE SCANNER
# ==========================================
st.markdown("### 🔍 Option 1: Quick Barcode Scan")
barcode = st.text_input("Enter Product Barcode (e.g., 049000000443 for Sprite):")

if st.button("Scan Barcode"):
    if barcode:
        with st.spinner("Fetching factual data from Open Food Facts..."):
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            headers = {"User-Agent": "NutraDecode_Portfolio_App/1.0"}
            try:
                response = requests.get(url, headers=headers)
                data = response.json() 
                if data.get("status") == 1:
                    product = data["product"]
                    st.success("Product found!")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        image_url = product.get("image_url", "")
                        if image_url:
                            st.image(image_url, use_column_width=True)
                    with col2:
                        st.subheader(product.get("product_name", "Unknown Product"))
                        st.info(f"**Ingredients:** {product.get('ingredients_text', 'None listed.')}")
                        additives = product.get("additives_tags", [])
                        if additives:
                            clean_additives = [add.replace("en:", "").upper() for add in additives]
                            st.table({"Chemical Additives": clean_additives})
                else:
                    st.info("We couldn't find this barcode. Scroll down to use the Label Decoder instead! 👇")
            except Exception as e:
                st.error("Database unavailable. Please use the Label Decoder below.")
    else:
        st.warning("Please enter a barcode first.")

st.markdown("---")

# ==========================================
# TOOL 2: THE LABEL DECODER
# ==========================================
st.markdown("### 🧠 Option 2: Label Decoder")
st.markdown("Upload a picture of the ingredients, or type the product name to have it decoded.")

# User Choices
category = st.radio("1. What are we scanning today?", ("💊 Supplements / Medicine", "🍎 Food Products / Snacks"))
upload_type = st.radio("2. How do you want to input the product?", ("📸 Upload an Image", "⌨️ Type the Product Name"))

user_image = None
product_name = ""

if upload_type == "📸 Upload an Image":
    uploaded_file = st.file_uploader("Upload a photo of the product front or label...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Uploaded Image", use_column_width=True)
else:
    product_name = st.text_input("Enter the exact product name (e.g., 'Oreo Cookies' or 'Advil'):")

# Your Master Prompt
system_prompt = f"""
You are "NutraDecode," an expert Food Scientist and Pharmacist scanner app.

CRITICAL RULE: If the user provides a product name or an image of the FRONT of a package, you MUST use your extensive knowledge base to fetch the exact, official ingredient list for that specific product before answering. Do not guess. Do not say "likely uses." State the actual ingredients.

The user has selected the category: {category}

If the category is 💊 Supplements / Medicine, format your EXACT output like this:
💊 **Product:** [Name]
**Primary Purpose:** [Explain what it treats/does in 2 sentences]

🔬 **What's Inside & Why (Active Ingredients):**
- **[Ingredient Name] ([Dose]):** [What it does]
- *(Note on Inactive Ingredients):* [Mention any dyes or fillers]

⚠️ **Who Should Avoid This:**
- [List specific medical conditions, e.g., Diabetics, pregnant women, and explain WHY.]

⏱️ **When & How to Consume:**
- **Best Time:** [Empty stomach, with food, etc.]
- **Pro Tip:** [Any tip like taking with Vitamin C]

⚖️ **Dosage:**
- **Label Instruction:** [What the label says]

🚫 **What NOT to take alongside this:**
- [List 2-3 common drug/food interactions].

If the category is 🍎 Food Products / Snacks, format your EXACT output like this:
🍎 **Product:** [Name]

🎯 **The Claim Check:**
- **Claims Identified:** [Identify marketing claims like "Zero Sugar"]
- **The Scientific Truth:** [Expose the truth based on exact ingredients. E.g., "Uses Maltodextrin which spikes blood sugar"]

🔬 **Exact Ingredient Breakdown:**
- **[Ingredient Name]:** [Why did the food scientist add this?]

⚠️ **Who Should Avoid This:**
- [List specific people, e.g., "Diabetics: Beware of Maltodextrin"]

⚖️ **Serving Size & When to Consume:**
- [Serving size context and best time to eat it].
"""

if st.button("Decode ✨"):
    if not api_key:
        st.error("API Key missing! Please check your Streamlit secrets.")
    elif user_image is None and product_name == "":
        st.warning("Please upload an image or type a product name first!")
    else:
        with st.spinner("Analyzing product scientifically..."):
            try:
                # Send data to AI
                if user_image is not None:
                    response = model.generate_content([system_prompt, user_image])
                else:
                    response = model.generate_content(f"{system_prompt}\n\nProduct Name: {product_name}")
                
                # Show result
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
