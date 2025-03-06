from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.models.schemas import CityCreate
from app.core.database import cities_collection
from app.utils.helpers import serialize_mongo_doc

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_city(city: CityCreate):
    city_dict = city.dict()
    city_dict["country_id"] = ObjectId(city_dict["country_id"])
    result = await cities_collection.insert_one(city_dict)
    created_city = await cities_collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_city)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_cities(country_id: Optional[str] = None):
    filter_query = {}
    if country_id:
        filter_query["country_id"] = ObjectId(country_id)
    
    cities = await cities_collection.find(filter_query).to_list(100)
    
    for city in cities:
        city["id"] = str(city["_id"])
        if "country_id" in city and isinstance(city["country_id"], ObjectId):
            city["country_id"] = str(city["country_id"])
    
    return [serialize_mongo_doc(city) for city in cities]

@router.get("/{city_id}", response_model=Dict[str, Any])
async def get_city(city_id: str):
    city = await cities_collection.find_one({"_id": ObjectId(city_id)})
    if city:
        return serialize_mongo_doc(city)
    raise HTTPException(404, "City not found")