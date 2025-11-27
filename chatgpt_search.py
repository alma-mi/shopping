"""
ChatGPT Image Analysis for Product Search
Uses Azure OpenAI GPT-4 Vision API to analyze images and extract search terms
"""
import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv

PHARAMS_FIRST = 0
load_dotenv()


def encode_image_to_base64(image_path):
    """
    Encode image file to base64 string
    Args:
        image_path: Path to the image file
    Returns:
        Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image_bytes_to_base64(image_bytes):
    """
    Encode image bytes to base64 string
    Args:
        image_bytes: Image data as bytes
    Returns:
        Base64 encoded string of the image
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def analyze_image_for_products(image_path=None, image_bytes=None):
    """
    Analyze image using Azure OpenAI GPT-4 Vision.

    Extract product search terms from image.

    Args:
        image_path: Path to the image file (optional)
        image_bytes: Image data as bytes (optional)

    Returns:
        tuple: (search_terms, error_message)
            - search_terms: Extracted search terms or None
            - error_message: Error message or None if successful
    """
    try:
        # Get Azure OpenAI configuration from environment
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )
        deployment_name = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"
        )

        if not azure_endpoint:
            err_msg = "AZURE_OPENAI_ENDPOINT not found in env vars"
            return None, err_msg + ". Please add it to .env file"

        if not api_key:
            err_msg = "AZURE_OPENAI_API_KEY not found in env vars"
            return None, err_msg + ". Please add it to .env file"

        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )

        # Encode image to base64
        if image_path:
            base64_image = encode_image_to_base64(image_path)
        elif image_bytes:
            base64_image = encode_image_bytes_to_base64(image_bytes)
        else:
            return None, "No image provided"

        # Create the prompt for GPT-4 Vision
        prompt = (
            "Analyze this image and identify products, items, or "
            "objects someone might want to purchase.\n"
            "\nYour task:\n"
            "1. Identify main product(s) or item(s)\n"
            "2. Note key characteristics (brand, color, etc)\n"
            "3. Extract relevant search terms for this product\n"
            "\nProvide a concise search query (2-6 words).\n"
            "Only return search terms. Make it specific for e-comm.\n"
            "\nExamples:\n"
            "- Red Nike shoe: 'red Nike running shoes'\n"
            "- Laptop: 'silver laptop computer'\n"
            "- Coffee maker: 'stainless steel coffee maker'\n"
            "\nReturn only the search query, no explanation."
        )

        # Call Azure OpenAI GPT-4 Vision API
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/jpeg;base64,"
                                    f"{base64_image}"
                                )
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0.3
        )

        # Extract search terms from response
        search_terms = (
            response.choices[PHARAMS_FIRST].message.content.strip()
        )

        # Clean up the response (remove quotes if present)
        search_terms = search_terms.strip('"').strip("'")

        return search_terms, None

    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        print(error_msg)
        return None, error_msg


def test_image_analysis():
    """Test function to verify image analysis works"""
    # Test with a sample image
    test_image = "test_image.jpg"

    if not os.path.exists(test_image):
        print(f"Test image '{test_image}' not found")
        msg = (
            "Place a test image named 'test_image.jpg' in "
            "the current directory"
        )
        print(msg)
        return

    print(f"Analyzing image: {test_image}")
    search_terms, error = analyze_image_for_products(image_path=test_image)

    if error:
        print(f"Error: {error}")
    else:
        print(f"Extracted search terms: {search_terms}")


if __name__ == "__main__":
    test_image_analysis()
