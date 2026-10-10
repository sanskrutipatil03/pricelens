
import re
import requests
import streamlit as st
from google import genai
from google.genai import types

from prompts import PRODUCT_IDENTIFICATION_PROMPT

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="SnapKhoj AI",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ SnapKhoj AI")
st.caption("One Snap. Every Deal.")
st.write(
    "Upload a product image to identify it with AI "
    "and compare available shopping prices."
)

# ---------------- API KEYS ----------------

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")

MODEL_NAME = "gemini-3.8-flash"


# ---------------- GEMINI CLIENT ----------------

@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)


# ---------------- PRODUCT IDENTIFICATION ----------------

def identify_product(image_bytes, mime_type, extra_details=""):
    client = get_gemini_client(GEMINI_API_KEY)

    prompt = f"""
    {PRODUCT_IDENTIFICATION_PROMPT}

    Additional details from user:
    {extra_details or "None"}
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        ]
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text


# ---------------- SHOPPING SEARCH ----------------

def search_products(query):
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY is missing from secrets.")

    response = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google_shopping",
            "q": query,
            "gl": "in",
            "hl": "en",
            "api_key": SERPAPI_KEY
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise ValueError(data["error"])

    return data.get("shopping_results", [])


# ---------------- PRICE PARSING ----------------

def extract_price(price_text):
    if not price_text:
        return None

    match = re.search(
        r"(?:₹|Rs\.?\s*)\s*([\d,]+(?:\.\d+)?)",
        str(price_text),
        re.IGNORECASE
    )

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


# ---------------- DISPLAY RESULTS ----------------

def display_results(products):
    if not products:
        st.warning("No shopping results found. Try another query.")
        return

    def sort_key(product):
        price = extract_price(product.get("price"))
        return (price is None, price if price is not None else float("inf"))

    products = sorted(products, key=sort_key)

    st.subheader("💰 Shopping Price Comparison")

    prices = [
        extract_price(product.get("price"))
        for product in products
    ]
    prices = [price for price in prices if price is not None]

    if prices:
        col1, col2 = st.columns(2)

        col1.metric("Lowest listed price", f"₹{min(prices):,.2f}")
        col2.metric("Highest listed price", f"₹{max(prices):,.2f}")

        if len(prices) >= 2:
            st.write(
                f"Price difference: ₹{max(prices) - min(prices):,.2f}"
            )

    for product in products:
        title = product.get("title", "Unknown product")
        price = product.get("price", "Not available")
        store = product.get("source", "Unknown store")
        delivery = product.get("delivery", "Not specified")
        link = product.get("product_link", "")

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**{title}**")
                st.write(f"Price: {price}")
                st.write(f"Store: {store}")
                st.caption(f"Delivery: {delivery}")

            with col2:
                if link.startswith(("https://", "http://")):
                    st.link_button("View product", link)
                else:
                    st.caption("Link unavailable")

    st.caption(
        "Prices may change. Confirm the exact model, delivery charges "
        "and final checkout price on the seller's website."
    )


# ---------------- CHECK CONFIGURATION ----------------

if not GEMINI_API_KEY:
    st.error("Add GEMINI_API_KEY to .streamlit/secrets.toml.")
    st.stop()


# ---------------- IMAGE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "📸 Upload a product image",
    type=["jpg", "jpeg", "png", "webp"]
)

extra_details = st.text_input(
    "Additional product details (optional)",
    placeholder="Example: Samsung Galaxy, 256 GB, black"
)

if uploaded_file:
    image_bytes = uploaded_file.getvalue()

    st.image(image_bytes, caption="Uploaded product", width=300)

    if st.button("🔍 Identify Product", type="primary"):
        try:
            with st.spinner("Gemini is analysing the image..."):
                st.session_state["product_info"] = identify_product(
                    image_bytes,
                    uploaded_file.type,
                    extra_details
                )
                st.session_state["shopping_query"] = ""

        except Exception as error:
            st.error(f"Identification failed: {error}")


# ---------------- SHOW PRODUCT DETAILS ----------------

if st.session_state.get("product_info"):
    st.subheader("🤖 Identified Product")
    st.write(st.session_state["product_info"])

    query = st.text_input(
        "Shopping search query",
        key="shopping_query",
        placeholder="Example: Samsung Galaxy S24 256 GB"
    )

    st.caption(
        "Review the model and edit the search query if necessary."
    )

    if st.button("🛒 Compare Prices", type="primary"):
        if not query.strip():
            st.warning("Enter a product name or model first.")

        elif not SERPAPI_KEY:
            st.error("Add SERPAPI_KEY to your secrets.")

        else:
            try:
                with st.spinner("Searching shopping listings..."):
                    results = search_products(query.strip())

                display_results(results)

            except requests.RequestException as error:
                st.error(f"Shopping request failed: {error}")

            except (ValueError, TypeError) as error:
                st.error(f"Could not process results: {error}")

            except Exception as error:
                st.error(f"Unexpected error: {error}")
