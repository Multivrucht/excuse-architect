import logging
from flask import current_app
from google import genai
from google.genai import types, errors

from excuse.excuse_gen_system_instructions import ExcuseGenMasterPrompt, ExcuseGenUserPrompt
from excuse.schema import ExcuseRequest
from service.exceptions import AIServiceAvailabilityError, AIServiceRequestError, RateLimitError


logger = logging.getLogger(__name__)

# This func is a good candidate for strategy pattern when introducing multiple providers
def generate_excuse(request: ExcuseRequest):
    """ Make call to gemini API """
    logger.info("API call started") 

    # The client gets the API key from the environment variable `GEMINI_API_KEY`
    client = genai.Client(api_key=current_app.config["GEMINI_API_KEY"])

    # Get master prompt
    sys_instructions = ExcuseGenMasterPrompt.BASE_TEMPLATE

    # Build user prompt
    user_input = ExcuseGenUserPrompt.build(request)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(system_instruction=sys_instructions), # type: ignore
            contents=user_input
        )

        return response.text
    
    except errors.APIError as e:
        # Will only catch API errors
        logger.error(f"Gemini API failed: {e.code} {e.details}") 
        
        if e.code == 429:
            raise RateLimitError("(Daily) Rate limit exceeded - try again later")
        elif 400 <= e.code < 500:
            raise AIServiceRequestError("Client request is incorrect")
        elif 500 <= e.code < 600:
            raise AIServiceAvailabilityError("AI service temporarily unavailable")
        else:
            raise Exception("Unspecified AI service error")