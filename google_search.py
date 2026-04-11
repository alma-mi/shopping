import os
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch
from constants import ONE, MAX_DISPLAY_RESULTS

# Load environment variables from .env file
load_dotenv()

ADD = ONE
MAX_RESULTS = MAX_DISPLAY_RESULTS

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


class GoogleSearchService:
    """Handles product searches using SerpAPI Google Shopping."""

    def google_search_for_product(self, product_name):
        products = []
        error_message = ""

        if product_name and SERPAPI_KEY:
            try:
                # Search for products using SerpAPI Google Shopping
                params = {
                    "engine": "google_shopping",
                    "q": product_name,
                    "api_key": SERPAPI_KEY,
                    "num": MAX_RESULTS
                }

                search = GoogleSearch(params)
                results = search.get_dict()

                if "shopping_results" in results:
                    for idx, item in enumerate(
                            results["shopping_results"][:MAX_RESULTS]):
                        product = {
                            "id": idx + ADD,
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
                elif "error" in results:
                    error_message = results["error"]
                else:
                    error_message = "No shopping results found."

            except Exception as e:
                error_message = f"Search error: {str(e)}"
        elif not SERPAPI_KEY:
            msg = "SerpAPI key not configured. Add SERPAPI_KEY to "
            error_message = msg + ".env file."

        return products, error_message


def google_search_for_product(product_name):
    """Module-level wrapper for backward compatibility."""
    return GoogleSearchService().google_search_for_product(product_name)
