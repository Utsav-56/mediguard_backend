from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import io

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API with the key from settings.py
genai.configure(api_key=GEMINI_API_KEY)

# Prompt for ai for medicine identification from image
PROMPT = ("Identify the medicine from its composition in the image and provide its compositions, scientific name, usage, "
          "and any important warnings. Be concise and accurate. if the medicine is not identified, respond with 'Unknown', "
          "also provide a confidence score. how much accuracy you are sure about the medicine identification. Generate the response in JSON format. with keys: name, compositions, usage, warnings, confidence_score.")

def process_uploaded_image(uploaded_file):
    """Process the uploaded image file and return a PIL Image object."""
    try:
        image = Image.open(io.BytesIO(uploaded_file.read()))
        return image
    except Exception as e:
        print(f"Error opening image: {e}")
        return None



# Response is most likely to be in md format, so we need to parse it accordingly
#  md json always starts and ends with ```json and ``` so we can extract the json part accordingly
def parse_md_json(md_content):
    """ Logic to parse json from md content
        My big brain said what if we just extract the part between ```json and ```
        and parse it as json
     """
    start_index = md_content.find('```json') + len('```json')
    end_index = md_content.rfind('```') - len('```')
    return md_content[start_index:end_index]


def identify_medicine_from_image(image):
    """Identify the medicine from the PIL Image object."""
    if image is None:
        return None

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([PROMPT, image])
        return parse_md_json(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

        
# // returns response and a boolean indicating success or failure
def validate_uploaded_file(request):
    """Validate the uploaded file in the request."""
    if 'image' not in request.FILES:
        return JsonResponse({
            'error': 'No image file provided',
            'success': False
        }, status=400), False
    
    uploaded_image = request.FILES['image']
    
    # Validate file type
    if not uploaded_image.content_type.startswith('image/'):
        return JsonResponse({
            'error': 'Invalid file type. Please upload an image.',
            'log' : f"Uploaded file type: {uploaded_image.content_type}, expected: image/*",
            'success': False
        }, status=400), False

    try:
     # Process the uploaded image
        image = process_uploaded_image(uploaded_image)
        
        if image is None:
            return JsonResponse({
                'error': 'Failed to process the uploaded image',
                'log': f"processed image is None",
                'success': False
            }, status=400), False
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred while processing the image: {str(e)}',
            'log': f"Error processing image: {str(e)}",
            'success': False
        }, status=500), False

    return image, True


@csrf_exempt
@require_http_methods(["POST"])
def upload_and_process_image(request):
    """Django view to handle image upload and process it for medicine identification."""

    image, is_valid = validate_uploaded_file(request)

    if not is_valid:
        return image  # image contains the JsonResponse in case of error

    try:
        # Identify medicine from the image
        result = identify_medicine_from_image(image)
        
        if result:
            try:
                # Try to parse the JSON response from Gemini
                medicine_info = json.loads(result)
                return JsonResponse({
                    'success': True,
                    'data': medicine_info
                })

            except json.JSONDecodeError:
                # If response is not valid JSON, return as text
                return JsonResponse({
                    'success': True,
                    'data': {'response': result}
                })
        else:
            return JsonResponse({
                'error': 'Failed to identify medicine from the image',
                'log': f"""result is None or empty 
                \n result: {result} \n Potential cause can be: 
                1. No response from Gemini API
                2. Gemini API Trial limit exceeded
                
                """,
                'success': False
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred while processing the image: {str(e)}',
            'success': False
        }, status=500)

