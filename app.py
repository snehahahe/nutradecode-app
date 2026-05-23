import streamlit as st
import requests

# 1. Set up the page (Default font)
st.set_page_config(page_title="NutraDecode", page_icon="🍃", layout="centered")

st.title("🍃 NutraDecode")
st.markdown("**Your transparent, product label decoder.**")
st.markdown("Enter a product barcode below to pull **real, factual data** directly from global food databases.")
st.markdown("---")

# 2. Create the search bar
barcode = st.text_input("Enter Product Barcode (e.g., 049000000443 for Sprite):")

# 3. What happens when the user clicks the button
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
