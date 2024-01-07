from dotenv import load_dotenv
from starlette.config import Config

config = Config(".env")

load_dotenv()

ENVIRONMENT = config("ENVIRONMENT", default="local")
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
SQLALCHEMY_DATABASE_URI = config("SQLALCHEMY_DATABASE_URI", str)
ELASTICSEARCH_URL = config("ELASTICSEARCH_URL", str)
ELASTICSEARCH_API_KEY = config("ELASTICSEARCH_API_KEY", str)
