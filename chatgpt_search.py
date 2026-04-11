"""
ChatGPT Image Analysis for Product Search
Uses Azure OpenAI GPT-4 Vision API to analyze images and extract search terms
"""
import io
import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv
from PIL import Image
from constants import PARAMS_FIRST, GPT4_MAX_TOKENS, GPT4_TEMPERATURE

PHARAMS_FIRST = PARAMS_FIRST
load_dotenv()


class ChatGPTSearchService:
    """Analyzes images with Azure OpenAI GPT-4 Vision to extract product search terms."""

    def encode_image_to_base64(self, image_path):
        """
        Encode image file to base64 string
        Args:
            image_path: Path to the image file
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Formats supported by the OpenAI vision API
    OPENAI_SUPPORTED_FORMATS = {'jpeg', 'png', 'gif', 'webp'}
    OPENAI_MIME_TYPES = {
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
    }

    def encode_image_bytes_to_base64(self, image_bytes):
        """
        Encode image bytes to base64 string, converting unsupported
        formats (e.g. BMP) to PNG first.
        Args:
            image_bytes: Image data as bytes
        Returns:
            tuple: (base64_string, mime_type)
        """
        img = Image.open(io.BytesIO(image_bytes))
        fmt = (img.format or '').lower()
        if fmt not in self.OPENAI_SUPPORTED_FORMATS:
            # Convert to PNG
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            image_bytes = buf.getvalue()
            fmt = 'png'
        mime_type = self.OPENAI_MIME_TYPES[fmt]
        return base64.b64encode(image_bytes).decode('utf-8'), mime_type

    def analyze_image_for_products(self, image_path=None, image_bytes=None):
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
            # Step 1: Initialize Azure client
            client = self._init_azure_client()
            if isinstance(client, tuple):
                return client

            # Step 2: Encode image to base64
            encode_result = self._encode_image(image_path, image_bytes)
            if isinstance(encode_result, tuple) and encode_result[0] is None:
                return encode_result
            base64_image, mime_type = encode_result

            # Step 3: Get analysis prompt
            prompt = self._get_analysis_prompt()

            # Step 4: Call GPT-4 Vision API
            response = self._call_gpt4_api(client, prompt,
                                           base64_image, mime_type)

            # Step 5: Extract and clean search terms
            search_terms = self._extract_search_terms(response)

            return search_terms, None

        except Exception as e:
            error_msg = f"Error analyzing image: {str(e)}"
            print(error_msg)
            return None, error_msg

    def _init_azure_client(self):
        """
        Initialize Azure OpenAI client with environment configuration.

        Returns:
            AzureOpenAI client or (None, error_message) tuple
        """
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )

        if not azure_endpoint:
            err_msg = "AZURE_OPENAI_ENDPOINT not found in env vars"
            return None, err_msg + ". Please add it to .env file"

        if not api_key:
            err_msg = "AZURE_OPENAI_API_KEY not found in env vars"
            return None, err_msg + ". Please add it to .env file"

        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )

        return client

    def _encode_image(self, image_path=None, image_bytes=None):
        """
        Encode image to base64 from file path or bytes.

        Args:
            image_path: Path to image file (optional)
            image_bytes: Image bytes (optional)

        Returns:
            (base64_string, mime_type) or (None, error_message) tuple
        """
        if image_path:
            with open(image_path, 'rb') as f:
                raw = f.read()
            return self.encode_image_bytes_to_base64(raw)
        elif image_bytes:
            return self.encode_image_bytes_to_base64(image_bytes)
        else:
            return None, "No image provided"

    def _get_analysis_prompt(self):
        """Get the GPT-4 Vision analysis prompt."""
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
        return prompt

    def _call_gpt4_api(self, client, prompt, base64_image,
                       mime_type='image/jpeg'):
        """
        Call Azure OpenAI GPT-4 Vision API with image and prompt.

        Args:
            client: AzureOpenAI client
            prompt: Analysis prompt text
            base64_image: Base64 encoded image
            mime_type: MIME type of the image (e.g. 'image/png')

        Returns:
            API response
        """
        deployment_name = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"
        )

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
                                    f"data:{mime_type};base64,"
                                    f"{base64_image}"
                                )
                            }
                        }
                    ]
                }
            ],
            max_tokens=GPT4_MAX_TOKENS,
            temperature=GPT4_TEMPERATURE
        )

        return response

    def _extract_search_terms(self, response):
        """
        Extract and clean search terms from API response.

        Args:
            response: API response object

        Returns:
            Cleaned search terms string
        """
        search_terms = (
            response.choices[PHARAMS_FIRST].message.content.strip()
        )
        # Remove surrounding quotes if present
        search_terms = search_terms.strip('"').strip("'")
        return search_terms

    def test_image_analysis(self):
        """Test function to verify image analysis works"""
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
        search_terms, error = self.analyze_image_for_products(
            image_path=test_image)

        if error:
            print(f"Error: {error}")
        else:
            print(f"Extracted search terms: {search_terms}")


def encode_image_to_base64(image_path):
    """Module-level wrapper for backward compatibility."""
    return ChatGPTSearchService().encode_image_to_base64(image_path)


def encode_image_bytes_to_base64(image_bytes):
    """Module-level wrapper for backward compatibility."""
    return ChatGPTSearchService().encode_image_bytes_to_base64(image_bytes)


def analyze_image_for_products(image_path=None, image_bytes=None):
    """Module-level wrapper for backward compatibility."""
    return ChatGPTSearchService().analyze_image_for_products(
        image_path, image_bytes)


if __name__ == "__main__":
    ChatGPTSearchService().test_image_analysis()
