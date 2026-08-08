from __future__ import annotations

import logging
import random

from flask import current_app
from google import genai
from google.genai import types, errors

from enum import Enum
from excuse.excuse_gen_system_instructions import ExcuseGenMasterPrompt, ExcuseGenUserPrompt
from excuse.excuse_request_models import UserExcuseInput
from service.exceptions import AIServiceAvailabilityError, AIServiceRequestError, RateLimitError
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class Provider(ABC):
    
    @abstractmethod
    def request_excuse(self, request: UserExcuseInput) -> str:
        ...


class MockProvider(Provider):

    def request_excuse(self, request: UserExcuseInput) -> str:
        """ Mock API rsponse for testing/demo purpose. """
        logger.info("Using mock API")
        
        random_answers = {  
            0: "Yeah, I wasn't able to do that due to a Windows update loop.",
            1: "I left too late because I didnt want to come",
            2: "My apologies for the missed deadline. I experienced an unexpected personal capacity constraint that impacted my ability to finalize the deliverable. I take full responsibility and will ensure prompt submission.",
            3: "My sincere apologies for the delayed response. I regrettably overlooked your email amidst a high volume of priority tasks this past week. Thank you for your patience.",
            4: "The timeline shifted due to incomplete initial requirements. While I adjusted, this naturally impacted deliverables, which, as experienced professionals, I assume we all understand."}
        
        randomnumber = random.randrange(0,4,1)
        answer = random_answers.get(randomnumber)

        return str(answer)


class GeminiProvider(Provider):

    def request_excuse(self, request: UserExcuseInput) -> str:
        """ Make call to gemini API """
        logger.info("Using Gemini API") 

        # The client gets the API key from the environment variable `GEMINI_API_KEY`
        client = genai.Client(api_key=current_app.config["GEMINI_API_KEY"])

        # Get master prompt & build user prompt
        sys_instructions = ExcuseGenMasterPrompt.BASE_TEMPLATE
        user_input = ExcuseGenUserPrompt.build(request)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                config=types.GenerateContentConfig(system_instruction=sys_instructions), # type: ignore
                contents=user_input
            )

            if response.text is None:
                 raise AIServiceAvailabilityError("AI service temporarily unavailable")
            return response.text
        
        except errors.APIError as e:
            # Will only catch API errors
            logger.error(f"Gemini API failed: {e.code} {e.details}") 
            
            
            # dive deeper into errors
            if e.code == 429:
                raise RateLimitError("(Daily) Rate limit exceeded - try again later")
            elif 400 <= e.code < 500:
                raise AIServiceRequestError("Client request is incorrect")
            elif 500 <= e.code < 600:
                raise AIServiceAvailabilityError("AI service temporarily unavailable")
            else:
                raise AIServiceRequestError("Unspecified AI service error")


           
class ProviderType(Enum):
    MOCK = MockProvider
    GEMINI = GeminiProvider

    
class ProviderSelector:
    
    def __init__(self) -> None:
        self._strategy: Provider = MockProvider()
    
    def set_strategy(self, strategy: ProviderType) -> None:
        if not isinstance(strategy, ProviderType):
            raise TypeError(f"Expected ProviderType, got {type(strategy).__name__}")
        
        inst = strategy.value()
        self._strategy = inst

        
    def request_excuse(self, request: UserExcuseInput) -> str:
        logger.info(f"Using Provider: {str(self._strategy)}")
        response = self._strategy.request_excuse(request)
        return response
