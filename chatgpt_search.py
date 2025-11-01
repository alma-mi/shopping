"""
ChatGPT Image Analysis for Product Search
Uses Azure OpenAI GPT-4 Vision API to analyze images and extract search terms
"""
import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
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
    Analyze image using Azure OpenAI GPT-4 Vision and extract product search terms
    
    Args:
        image_path: Path to the image file (optional)
        image_bytes: Image data as bytes (optional)
    
    Returns:
        tuple: (search_terms, error_message)
            - search_terms: String with extracted search terms or None if error
            - error_message: Error message or None if successful
    """
    try:
        # Get Azure OpenAI configuration from environment
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if not azure_endpoint:
            return None, "AZURE_OPENAI_ENDPOINT not found in environment variables. Please add it to .env file"
        
        if not api_key:
            return None, "AZURE_OPENAI_API_KEY not found in environment variables. Please add it to .env file"
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        # Encode image to base64
        if image_path:
            base64_image = encode_image_to_base64(image_path)
        elif image_bytes:
            base64_image = encode_image_bytes_to_base64(image_bytes)
        else:
            return None, "No image provided"
        
        # Create the prompt for GPT-4 Vision
        prompt = """Analyze this image and identify any products, items, or objects that someone might want to search for and purchase online.

Your task:
1. Identify the main product(s) or item(s) in the image
2. Note key characteristics (brand, color, type, model, etc.)
3. Extract the most relevant search terms that would help find this product online

Provide your response as a concise search query (2-6 words) that would be perfect for an online shopping search.
Only return the search terms, nothing else. Make it specific and relevant for e-commerce.

Examples:
- If you see a red Nike running shoe, return: "red Nike running shoes"
- If you see a laptop, return: "silver laptop computer"
- If you see a coffee maker, return: "stainless steel coffee maker"

Return only the search query, no explanation."""

        # Call Azure OpenAI GPT-4 Vision API
        response = client.chat.completions.create(
            model=deployment_name,  # Using Azure deployment name
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
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Extract search terms from response
        search_terms = response.choices[0].message.content.strip()
        
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
        print("Place a test image named 'test_image.jpg' in the current directory")
        return
    
    print(f"Analyzing image: {test_image}")
    search_terms, error = analyze_image_for_products(image_path=test_image)
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"Extracted search terms: {search_terms}")


if __name__ == "__main__":
    test_image_analysis()
