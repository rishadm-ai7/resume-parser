import os
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
APP_ENV = os.getenv("APP_ENV", "development")
