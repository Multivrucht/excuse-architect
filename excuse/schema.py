from pydantic import BaseModel, field_validator, Field

class ExcuseRequest(BaseModel):
    """ Excuse class object with Pydantic data validation """
    user_input: str = Field(min_length=1)
    blame: int = Field(ge=0, le=5)
    jargon: int = Field(ge=0, le=5)
    passive: int = Field(ge=0, le=5)
    vagueness: int = Field(ge=0, le=5)
    #_request_id: str ??
    
    @field_validator("user_input")
    def clean_input(cls, input): # pylint: disable=no-self-argument
        """ Remove whitespaces"""
        return input.strip()
