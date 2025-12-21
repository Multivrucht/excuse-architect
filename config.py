import os
from dotenv import load_dotenv

load_dotenv()

class ConfigBaseClass:
    """" Base class for setting env variable configurations. """

    # API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Flask
    PORT = int(os.getenv("PORT", "5000"))

    # Testing
    DEBUG = False
    USE_MOCK_API = False


class DevConfig(ConfigBaseClass):
    """ Dev settings palceholder. """
    ENV = "Development"
    USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() == "true"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    # GEMINI_API_KEY = os.getenv("FAKE_API_KEY")

class ProdConfig(ConfigBaseClass):
    """ Prod settings placeholder. """
    ENV = "Production"
    DEBUG = False
    USE_MOCK_API = False


config_map = {
    "dev": DevConfig,
    "prod": ProdConfig
}

def get_config() -> ConfigBaseClass:
    """ Get ENV type, either: dev | prod """
    env = os.getenv("FLASK_ENV", "dev")
    return config_map.get(env, DevConfig)