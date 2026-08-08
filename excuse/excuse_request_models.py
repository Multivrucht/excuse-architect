from uuid import UUID, uuid4  
from datetime import datetime

from pydantic import BaseModel, field_validator, Field, ConfigDict

class UserExcuseInput(BaseModel):
    """ Excuse class object with Pydantic data validation """
    
    model_config = ConfigDict(extra="forbid")
    
    user_input: str = Field(min_length=1, max_length=250)
    blame: int = Field(0, ge=0, le=5)
    jargon: int = Field(0, ge=0, le=5)
    passive: int = Field(0, ge=0, le=5)
    vagueness: int = Field(0, ge=0, le=5)
    
    @field_validator("user_input")
    def clean_input(cls, user_input: str): # pylint: disable=no-self-argument
        text = user_input.strip()
        text = text.strip("'\\/\"") # future: add llm safety cleaning
        return text


class UserRequestMetaData(BaseModel):
    """ WIP: Connection data.."""
    timestamp: datetime = Field(default_factory=datetime.now)
    ip_address: str | None = None
    user_agent: str | None = None
    # requests_made: int
    # a user id to recognize the user?
    
class ExcuseRequestInternal(BaseModel):
    """ WIP: Excuse response model. """
    request_id: UUID = Field(default_factory=uuid4)
    excuse_request: UserExcuseInput | None
    metadata: UserRequestMetaData
    

class ExcuseRequestResponse(BaseModel):
    """ WIP: Response model for excuse request. """
    success: bool
    excuse: str | None = None
    error_message: str | None = None