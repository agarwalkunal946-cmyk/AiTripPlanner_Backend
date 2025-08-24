import google.generativeai as genai
import os
import json
import re
import logging
from fastapi import HTTPException
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
except Exception as e:
    logger.error(f"Error configuring Google Generative AI: {e}")
    raise

generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
    )
except Exception as e:
    logger.error(f"Error initializing Generative Model: {e}")
    raise

async def generate_trip_plan(prompt_data: dict):
    try:
        prompt = f"""
        Act as an expert travel agent. Generate a complete and detailed trip plan based on the user's criteria.
        Your response MUST be a single, valid JSON object and nothing else. Do not include any text before or after the JSON, and do not use markdown like ```json.

        The JSON object must contain the following keys:
        - "title": A creative and exciting title for the trip.
        - "destination": The primary destination city and country provided by the user.
        - "description": A short, engaging summary of the trip's theme and what to expect.
        - "duration_days": The number of days for the trip as an integer.
        - "price": An estimated budget for the trip in USD, excluding flights, as an integer.
        - "category": Choose the ONE most fitting category from this list: ["Adventure", "Cultural", "Relaxation", "Beach", "Mountain", "City"].
        - "difficulty_level": Choose the ONE most fitting difficulty level from this list: ["Easy", "Moderate", "Challenging", "Expert"].
        - "image_url": A URL for a high-quality, royalty-free stock photo from Unsplash that visually represents the trip (e.g., "https://images.unsplash.com/...").
        - "itinerary": An array of objects, where each object represents a single day. Each day object must have "day" (integer), "title" (string), and "activities" (array of strings).

        User Criteria:
        - Destination: {prompt_data['destination']}
        - Duration: {prompt_data['duration_days']} days
        - Budget Level: {prompt_data.get('budget', 'moderate')}
        - Interests: {', '.join(prompt_data.get('interests', []))}

        Ensure the generated values for 'category' and 'difficulty_level' are exactly as they appear in the provided lists.
        """
        
        logger.info("Generating content with prompt...")
        response = await model.generate_content_async(prompt)
        
        if not response.parts:
            logger.error("AI response was blocked or empty. Feedback: %s", response.prompt_feedback)
            raise HTTPException(
                status_code=500,
                detail="The AI failed to generate a response, possibly due to safety filters."
            )

        # Handle different response formats
        if hasattr(response.parts, 'text'):
            raw_text = response.parts.text
        elif hasattr(response, 'text'):
            raw_text = response.text
        else:
            # Try to get text from the first part
            raw_text = response.parts[0].text if response.parts else ""
            
        if not raw_text:
            logger.error("No text content found in AI response")
            raise HTTPException(
                status_code=500,
                detail="The AI response contained no text content."
            )
            
        logger.info(f"Raw response from AI: {raw_text}")

        cleaned_text = raw_text.strip().replace("```json", "").replace("```", "")
        
        json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        if not json_match:
            logger.error("No JSON object found in the AI response after cleaning.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate a valid trip plan. The AI response did not contain a JSON object."
            )
        
        json_string = json_match.group(0)
        
        return json.loads(json_string)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}. AI Response was: {json_string}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to parse the trip plan. The AI response was not valid JSON."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred while generating the AI plan: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {e}"
        )