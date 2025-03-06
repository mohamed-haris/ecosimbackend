import os
from dotenv import load_dotenv

load_dotenv()

API_TITLE = "Economic Simulation API"
API_VERSION = "2.0"

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "econ_simulator_db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")