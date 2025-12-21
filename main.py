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


# Import env variables
config = get_config()

# Set log conf
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="storage/system_log.log",
    filemode="a")

logger = logging.getLogger(__name__)

# Define app
app = Flask(__name__)
CORS(app) # Fix CORS later, sec flaw


@app.errorhandler(Exception)
def handle_unexpected(e) -> tuple[Response, int]:
    print("Unhandled error")
    logger.critical(f"Undefined error broke the system {e}")
    return jsonify({"success": False, "error_message": "Internal error"}), 500


@app.route("/api/submit", methods=["POST"])
def get_input() -> tuple[Response, int]:
    """ Main endpoint for the excuse generation, little too big atm, fix later """
    logger.info("/api/submit called")
    raw_data: dict = request.get_json()

    try:
        validated_req = ExcuseRequest(**raw_data) # Unpack dict into keyword
    except ValidationError as e:
        logger.warning(f"User input validation failed: {e}")
        return jsonify({"success": False, "error_message": "Client data not in required format"}), 400

    try:
        if config.USE_MOCK_API:
            logger.info("Using mock API")
            text = mock_call_text()
            response = { "success": True, "excuse": text }
        else:
            logger.info("Using Gemini API")
            excuse = generate_excuse(validated_req)
            write_to_file(excuse) # temp save to txt
            response = { "success": True, "excuse": excuse }

    except (RateLimitError, AIServiceRequestError, AIServiceAvailabilityError) as e:
        # Custom errors that are okay for users to see
        logger.error(f"Service failed: {e}")
        return jsonify({"success": False, "error_message": str(e)}) 

    except Exception as e:
        logger.error(f"Service failed: {e}")
        return jsonify({"success": False, "error_message": "Internal Error"}) 

    return jsonify(response), 200


if __name__ == "__main__":
    logger.info("Started Main Service..")
    app.run(debug=config.DEBUG, port=config.PORT)
