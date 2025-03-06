import motor.motor_asyncio
from app.core.config import MONGO_URL, DB_NAME

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

countries_collection = db.countries
cities_collection = db.cities
economic_parameters_collection = db.economic_parameters
city_profiles_collection = db.city_profiles
snapshots_collection = db.snapshots