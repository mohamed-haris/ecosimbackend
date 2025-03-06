from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.schemas import CityProfileCreate
from app.core.database import city_profiles_collection
from app.utils.helpers import serialize_mongo_doc

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_city_profile(profile: CityProfileCreate):
    profile_dict = profile.dict()
    profile_dict["city_id"] = ObjectId(profile_dict["city_id"])
    profile_dict["last_updated"] = datetime.now()
    
    for param in profile_dict["parameters"]:
        param["parameter_id"] = ObjectId(param["parameter_id"])
    
    result = await city_profiles_collection.insert_one(profile_dict)
    created_profile = await city_profiles_collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_profile)

@router.get("/{city_id}", response_model=Dict[str, Any])
async def get_city_profile(city_id: str):
    profile = await city_profiles_collection.find_one({"city_id": ObjectId(city_id)})
    if profile:
        return serialize_mongo_doc(profile)
    raise HTTPException(404, "City profile not found")