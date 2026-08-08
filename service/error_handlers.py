import logging
from difflib import get_close_matches

from flask import Flask, Response, jsonify
from pydantic import ValidationError

from werkzeug.exceptions import BadRequest, HTTPException
from excuse.excuse_request_models import UserExcuseInput


## still testing /start
MODEL_FIELDS = {
    "UserExcuseInput": list(UserExcuseInput.model_fields), #["user_input", "blame", "jargon", "passive", "vagueness"]
}

def unknown_field_message(field: str, valid_fields: list[str]) -> str:
    """ Message for an unrecognised field name, with a typo suggestion if one is close enough. """
    match = get_close_matches(field, valid_fields, n=1, cutoff=0.6)
    if match:
        return f"Unknown field. Did you mean '{match[0]}'?"
    return "Unknown field: not an accepted field name"


def build_error_details(e: ValidationError) -> list[dict]:
    """ Turn a Pydantic ValidationError into a safe, user-friendly list of errors. """
    
    valid_fields: list[str] = MODEL_FIELDS.get(e.title, []) #e.title = UserExcuseInput, where the model failed
    print(f"e errors are {e.errors()}")
    details = []
    for err in e.errors():
        field = ".".join(str(part) for part in err["loc"])
        if err["type"] == "extra_forbidden":
            message = unknown_field_message(field, valid_fields)
        else:
            message = err["msg"]
        details.append({"field": field, "message": message})
    return details

## still testing /end


def register_error_handlers(app: Flask, logger: logging.Logger):
    """ Register error handlers for the Flask app. """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError) -> tuple[Response, int]:
        logger.error("Validation error: %s", e)

        return jsonify({"success": False,
                        "error_message": "Invalid input data",
                        "details": build_error_details(e)}
                       ), 400

    @app.errorhandler(BadRequest)
    def handle_bad_request(e: BadRequest) -> tuple[Response, int]:
        logger.error("Bad request: %s", e)
        
        # Check for error safety..
        return jsonify({"success": False, 
                        "error_message": "Bad request", 
                        "details": str(e)}
                       ), 400
    
        # investigate this one further
        # @app.errorhandler(HTTPException)
        # def handle_http_exception(e: HTTPException) -> tuple[Response, int]:
        #     """Return HTTPExceptions (404, 405, etc.) as their proper status without alarming logs."""
        #     logger.warning("HTTP exception: %s", e)

        #     return jsonify({"success": False,
        #                     "error_message": e.description}
        #                    ), e.code
    
    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception) -> tuple[Response, int]:
        logger.exception("Unhandled system error: %s", e)
        
        return jsonify({"success": False, 
                        "error_message": "Internal error"}
                       ), 500