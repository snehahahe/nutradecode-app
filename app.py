import streamlit as st
import requests

# 1. WEB DESIGN MAGIC (Adding your custom fonts and colors)
custom_css = """
<style>
    /* Change the font of the entire app to Arial Unicode */
    html, body, [class*="css"]  {
        font-family: 'Arial Unicode MS', Arial, sans-serif !important;
    }
    
    /* Change the specific title font to TAN MON CHERIE */
    .custom-title {
        font-family: 'TAN MON CHERIE', 'Playfair Display', serif !important;
        font-size: 3.5rem;
        font-weight: bold;
        color: #2E4035; /* A dark, aesthetic, earthy green */
        margin-bottom: -10px;
    }
</style>
"""

# 2. Set up the page
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="centered")

# Inject the custom fonts into the app
st.markdown(custom_css, unsafe_allow_html=True)

# 3. The New Beautiful Custom Title
st.markdown('<p class="custom-title">🍃 NutraDecode</p>', unsafe_allow_html=True)
st.markdown("**Your transparent, AI-powered product label decoder.**")
st.markdown("Enter a product barcode below to pull **real, factual data** directly from global food databases.")
st.markdown("---")

# 4. Create the search bar
barcode = st.text_input("Enter Product Barcode (e.g., 049000000443 for Sprite):")

# 5. What happens when the user clicks the button
if st.button("Decode Product"):
    if barcode:
        with st.spinner("Fetching factual data from Open Food Facts..."):
            
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            headers = {"User-Agent": "NutraDecode_Portfolio_App/1.0"}
            
            try:
                response = requests.get(url, headers=headers)
                data = response.json() 
                
                # Check if the product exists
                if data.get("status") == 1:
                    product = data["product"]
                    
                    st.success("Product found!")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        image_url = product.get("image_url", "")
                        if image_url:
                            st.image(image_url, caption=product.get("product_name", "Product Image"), use_column_width=True)
                        else:
                            st.write("No image available.")
                    
                    with col2:
                        st.subheader(product.get("product_name", "Unknown Product"))
                        
                        st.markdown("### 📝 Factual Ingredients List")
                        st.info(product.get("ingredients_text", "No ingredient list found."))
                        
                        st.markdown("### 🧪 Chemical Additives Found")
                        additives = product.get("additives_tags", [])
                        if additives:
                            clean_additives = [add.replace("en:", "").upper() for add in additives]
                            st.table({"Additive Code": clean_additives})
                        else:
                            st.write("No additives detected.")
                            
                else:
                    # THE UX FIX: Your custom friendly message!
                    st.info("We couldn't find this barcode in the database. But don't worry! **Upload a picture of the ingredients**, or **type the product name**, and our AI will decode it for you right now.")
            
            except Exception as e:
                st.error("Oops! The global database is currently unavailable. Please try again later.")
    else:
        st.warning("Please enter a barcode first.")
