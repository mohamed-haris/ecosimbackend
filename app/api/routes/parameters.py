from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from app.models.schemas import EconomicParameterCreate
from app.core.database import economic_parameters_collection
from app.utils.helpers import serialize_mongo_doc

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_parameter(parameter: EconomicParameterCreate):
    result = await economic_parameters_collection.insert_one(parameter.dict())
    created_parameter = await economic_parameters_collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_parameter)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_parameters(category: Optional[str] = None):
    filter_query = {}
    if category:
        filter_query["category"] = category
    
    parameters = await economic_parameters_collection.find(filter_query).to_list(100)
    return [serialize_mongo_doc(param) for param in parameters]