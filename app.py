import streamlit as st
import requests

# 1. Set up the aesthetic look of the website
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="centered")

st.title("🍃 NutraDecode")
st.markdown("**Your transparent, AI-powered product label decoder.**")
st.markdown("Enter a product barcode below to pull **real, factual data** directly from global food databases, avoiding AI hallucinations.")

# 2. Create the search bar
barcode = st.text_input("Enter Product Barcode (e.g., 049000000443 for Sprite):")

# 3. What happens when the user clicks the button
if st.button("Decode Product"):
    if barcode:
        with st.spinner("Fetching factual data from Open Food Facts..."):
            
            # Fetch data from the free API
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url).json()
            
            # Check if the product exists
            if response.get("status") == 1:
                product = response["product"]
                
                st.success("Product found!")
                
                # Create two columns for a beautiful layout
                col1, col2 = st.columns([1, 2])
                
                # Column 1: Aesthetic Product Image
                with col1:
                    image_url = product.get("image_url", "")
                    if image_url:
                        st.image(image_url, caption=product.get("product_name", "Product Image"), use_column_width=True)
                    else:
                        st.write("No image available.")
                
                # Column 2: Factual Data & Tables
                with col2:
                    st.subheader(product.get("product_name", "Unknown Product"))
                    
                    st.markdown("### 📝 Factual Ingredients List")
                    st.info(product.get("ingredients_text", "No ingredient list found."))
                    
                    st.markdown("### ⚠️ Allergens & Warnings")
                    st.warning(product.get("allergens", "None listed."))
                    
                    # A sleek table for Additives / EU/FDA data
                    st.markdown("### 🧪 Chemical Additives Found")
                    additives = product.get("additives_tags", [])
                    if additives:
                        # Clean up the text for the table
                        clean_additives = [add.replace("en:", "").upper() for add in additives]
                        st.table({"Additive Code": clean_additives})
                    else:
                        st.write("No additives detected.")
                        
            else:
                st.error("Product not found in the global database. Please try another barcode.")
    else:
        st.warning("Please enter a barcode first.")
