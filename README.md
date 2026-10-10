SnapKhoj AI 🛍️

AI-Powered Visual Product Search and Price Comparison

📌 About the Project

SnapKhoj AI is an AI-powered application that helps users identify products from images and find shopping listings with prices from online shopping sources.

Users can upload a product image, identify the product using AI, and search for available shopping options to compare prices.

✨ Key Features

Image-Based Product Identification: Upload an image of a product for AI-powered identification.

Product Details: Display the product name, brand, model, and identifiable specifications when available.

Shopping Search: Search for matching products using Google Shopping results.

Price Comparison: View available prices and product links from shopping listings.

Simple User Interface: Use the application through a Streamlit web interface.

🛠️ Technologies Used

Python

Streamlit

Google Gemini AI (Vision)

SerpAPI (Google Shopping Search)

⚙️ How It Works

Upload a product image.

Gemini AI analyses the image and identifies the product.

Enter or review the relevant product search query.

SnapKhoj AI retrieves available shopping listings.

Compare displayed prices and open seller links to review the products.

🚀 How to Run the Project

Clone this repository.

Open the project folder in VS Code.

Create and activate a Python virtual environment.

Install the required packages using pip install -r requirements.txt.

Configure your Gemini API key and SerpAPI key in Streamlit secrets.

Run the application:

python -m streamlit run app.py

🔐 API Configuration

Configure the required API keys locally in .streamlit/secrets.toml:

GEMINI_API_KEY

SERPAPI_KEY

Never upload API keys or secret credentials to GitHub.

⚠️ Disclaimer

Product identification and shopping prices may not always be exact. Verify the product model, specifications, seller details, and final price on the shopping website before purchasing.

🔮 Future Improvements

Improve exact product and model matching.

Add product-category-specific specifications.

Enhance price comparison and filtering.

Improve the user interface and shopping experience.

