"""
Main server code, used for running server
"""

import logging
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError
from config import get_config
from AI.gemini_call import generate_excuse
from service.write_to_file import write_to_file
from tests.mock_basic_api_call import mock_call_text
from excuse.schema import ExcuseRequest
from service.exceptions import AIServiceAvailabilityError, AIServiceRequestError, RateLimitError




def create_app() -> Flask:
    """ Creates the Flask app and configures it.
        
        Refactor:
            Fix CORS
            cofnig override parameter for custom test configs?
            Seperate routes and exceptions"""

    # Import env variables
    config = get_config()

    # Define app
    app = Flask(__name__)

    # Copy to flask config 
    app.config.from_object(config)

    # Set CORS, FIX LATER SEC FLAW
    CORS(app)


    # Set log conf
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filename="storage/system_log.log",
        filemode="a")

    logger = logging.getLogger(__name__)
    logger.info(f"App started in {app.config["ENV"]} mode")



    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception) -> tuple[Response, int]:
        print(f"TESTING: Unhandled error {e}")
        logger.critical(f"Undefined error broke the system {e}")
        return jsonify({"success": False, "error_message": "Internal error"}), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError) -> tuple[Response, int]:
        logger.warning(f"User input validation failed: {e}")
        return jsonify({"success": False, "error_message": "Client data not in required format"}), 400



    @app.route("/health")
    def health() -> tuple[Response, int]:
        """ Test endpoint """
        logger.info("/health called")
        return jsonify({"succes:": True, "message": "OK"}), 200


    @app.route("/api/submit", methods=["POST"])
    def get_input() -> tuple[Response, int]:
        """ Main endpoint for the excuse generation, little too big atm, fix later """
        logger.info("/api/submit called")

        raw_data: dict = request.get_json()
        validated_req = ExcuseRequest(**raw_data) # Unpack dict into keyword

        try:
            if app.config["USE_MOCK_API"]:
                logger.info("Using mock API")
                text = mock_call_text()
                response = { "success": True, "excuse": text }
            else:
                logger.info("Using Gemini API")
                excuse = generate_excuse(validated_req)
                write_to_file(excuse) # temp save to txt
                response = { "success": True, "excuse": excuse }

        except (RateLimitError, AIServiceRequestError, AIServiceAvailabilityError) as e:
            # E has custom errors that are okay for users to see
            logger.error(f"Service failed: {e}")
            return jsonify({"success": False, "error_message": str(e)}), e.status_code

        return jsonify(response), 200

    return app

# Create app
app = create_app()

if __name__ == "__main__":
    # DEV server
    logger = logging.getLogger(__name__)
    logger.info("Starting Flask dev server")
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"])
    # app.config["FLASK_ENV"] = "dev"