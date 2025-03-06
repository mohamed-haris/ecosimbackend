from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from bson import ObjectId
from app.models.schemas import CountryCreate
from app.core.database import countries_collection
from app.utils.helpers import serialize_mongo_doc

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_country(country: CountryCreate):
    result = await countries_collection.insert_one(country.dict())
    created_country = await countries_collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_country)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_countries():
    countries = await countries_collection.find().to_list(100)
    return [serialize_mongo_doc(country) for country in countries]

@router.get("/{country_id}", response_model=Dict[str, Any])
async def get_country(country_id: str):
    country = await countries_collection.find_one({"_id": ObjectId(country_id)})
    if country:
        return serialize_mongo_doc(country)
    raise HTTPException(404, "Country not found")