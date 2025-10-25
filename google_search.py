import os
from serpapi import GoogleSearch

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def google_search_for_product(product_name):
    products = []
    error_message = ""
    
    if product_name and SERPAPI_KEY:
        try:
            # Search for products using SerpAPI Google Shopping
            params = {
                "engine": "google_shopping",
                "q": product_name,
                "api_key": SERPAPI_KEY,
                "num": 10  # Limit to 10 results
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "shopping_results" in results:
                for idx, item in enumerate(results["shopping_results"][:10]):
                    product = {
                        "id": idx + 1,
                        "name": item.get("title", "Unknown Product"),
                        "price": item.get("price", "Price not available"),
                        "source": item.get("source", "Unknown"),
                        "link": item.get("link", "#"),
                        "product_link": item.get("product_link", "#"),
                        "thumbnail": item.get("thumbnail", ""),
                        "rating": item.get("rating", 0),
                        "reviews": item.get("reviews", 0)
                    }
                    products.append(product)
            else:
                error_message = "No shopping results found."
                
        except Exception as e:
            error_message = f"Search error: {str(e)}"
    elif not SERPAPI_KEY:
        error_message = "SerpAPI key not configured. Please add SERPAPI_KEY to your .env file."    

    return products, error_message