import logging
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError
from config import get_config
from AI.request_providers import ProviderSelector, ProviderType
from service.write_to_file import write_to_file
from service.error_handlers import register_error_handlers
from excuse.excuse_request_models import UserExcuseInput, UserRequestMetaData, ExcuseRequestInternal
from service.exceptions import UserFacingErrors


# Set log conf
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="storage/system_log.log",
    filemode="a")

logger = logging.getLogger(__name__)


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
    
    
    # set provider, still need to adjust config class properly
    provider = ProviderSelector()
    if not app.config["USE_MOCK_API"]:
        provider.set_strategy(ProviderType.GEMINI)

    # Set CORS, FIX LATER SEC FLAW
    CORS(app)

    register_error_handlers(app, logger)

    logger.info(f"App started in {app.config['ENV']} mode")


    @app.route("/health")
    def health() -> tuple[Response, int]:
        """ Test endpoint """
        logger.info("/health called")
        return jsonify({"success:": True, 
                        "message": "OK"}), 200


    @app.route("/submit", methods=["POST"])
    def get_input() -> tuple[Response, int]:
        """ Main endpoint for the excuse generation, little too big atm, fix later """
        logger.info("/submit called")

        # put in sep helper method
        connection_data = UserRequestMetaData(
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "unknown")
        )
        
        #  Maybe check for deseral errs here?
        raw_data: dict = request.get_json()
        
        try:
            validated_req = UserExcuseInput(**raw_data)
            
        except ValidationError as error:
            # implement some failure logging..
            
            # attempt = AttemptedExcuseRequest(raw_request=raw_data, parsed_request=None, validation_errors=e.errors(), metadata=connection_data)
            # save_attempt(attempt)
            # logger.warning("validation failed %s", attempt.request_id)
            
            # separate model here?
            # internal = ExcuseRequestInternal(
            #     excuse_request=None,
            #     metadata=connection_data)
            # print(f"failed: validation {internal}")
            # raise error for further handling
            raise error
        else:
            internal = ExcuseRequestInternal(
                excuse_request=validated_req,
                metadata=connection_data)
            
            print(f"valdiated succesful {internal}")
            
        try:
            excuse = provider.request_excuse(internal.excuse_request)
            write_to_file(excuse) # write to proper db
            response = { "success": True, "excuse": excuse }
            return jsonify(response), 200
        
        except UserFacingErrors as e:
            # E has custom errors that are okay for users to see
            logger.error("Service failed: %s", e)
            return jsonify({"success": False, 
                            "error_message": str(e)}), e.status_code

    return app

# Create app
app = create_app()

if __name__ == "__main__":
    # DEV server
    logger = logging.getLogger(__name__)
    print("Running flask..")
    #   print(f"App config: {app.config}")
    logger.info("Starting Flask dev server")
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"])
    # app.config["FLASK_ENV"] = "dev"
