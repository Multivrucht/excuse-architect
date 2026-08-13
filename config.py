import os
from dotenv import load_dotenv


load_dotenv()

class ConfigBaseClass:
    """ Base class for setting env variable configurations. """
    def __init__(self) -> None:
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.PORT = int(os.getenv("PORT", "5200"))
        self.DEBUG = False
        self.USE_MOCK_API = False


class DevConfig(ConfigBaseClass):
    """ Dev settings palceholder. """
    def __init__(self) -> None:
        super().__init__()
        self.ENV = "Development"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() == "true"
        
        if self.USE_MOCK_API:
            self.GEMINI_API_KEY = "UNSET"

class ProdConfig(ConfigBaseClass):
    """ Prod settings placeholder. """
    def __init__(self) -> None:
        super().__init__()
        self.ENV = "Production"
        self.USE_MOCK_API = False

        if not self.GEMINI_API_KEY:
            raise RuntimeError("MISSING GEMINIAPIKEY")

config_map = {
    "dev": DevConfig,
    "prod": ProdConfig
}

def get_config() -> ConfigBaseClass:
    """ Get ENV type, either: dev | prod """
    env = os.getenv("FLASK_ENV")
    if env not in config_map:
        raise RuntimeError(f"Unknown Environment for given FLASK_ENV value:{env}")
    return config_map[env]()