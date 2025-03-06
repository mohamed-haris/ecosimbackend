from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.models.schemas import SnapshotCreate, SimulationAdvance
from app.core.database import snapshots_collection, city_profiles_collection
from app.utils.helpers import serialize_mongo_doc
from app.services.simulation import calculate_economic_health
from app.services.ai_analysis import generate_ai_analysis

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_snapshot(snapshot: SnapshotCreate):
    snapshot_dict = snapshot.dict()
    snapshot_dict["city_id"] = ObjectId(snapshot_dict["city_id"])
    snapshot_dict["created_at"] = datetime.now()
    snapshot_dict["is_completed"] = False
    snapshot_dict["results"] = []
    
    for stage in snapshot_dict["stages"]:
        for param in stage["parameters"]:
            param["parameter_id"] = ObjectId(param["parameter_id"])
    
    result = await snapshots_collection.insert_one(snapshot_dict)
    created_snapshot = await snapshots_collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_snapshot)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_snapshots(city_id: Optional[str] = None):
    filter_query = {}
    if city_id:
        filter_query["city_id"] = ObjectId(city_id)
    
    snapshots = await snapshots_collection.find(filter_query).to_list(100)
    return [serialize_mongo_doc(snapshot) for snapshot in snapshots]

@router.get("/{snapshot_id}", response_model=Dict[str, Any])
async def get_snapshot(snapshot_id: str):
    snapshot = await snapshots_collection.find_one({"_id": ObjectId(snapshot_id)})
    if snapshot:
        return serialize_mongo_doc(snapshot)
    raise HTTPException(404, "Snapshot not found")

@router.post("/{snapshot_id}/simulate", response_model=Dict[str, Any])
async def simulate_snapshot(snapshot_id: str):
    snapshot = await snapshots_collection.find_one({"_id": ObjectId(snapshot_id)})
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    
    city_profile = await city_profiles_collection.find_one({"city_id": snapshot["city_id"]})
    if not city_profile:
        raise HTTPException(404, "City profile not found")
    
    current_values = {}
    for param in city_profile["parameters"]:
        current_values[str(param["parameter_id"])] = param["base_value"]
    
    results = []
    term_counter = 1
    
    for stage in snapshot["stages"]:
        growth_rates = {}
        for param in stage["parameters"]:
            growth_rates[str(param["parameter_id"])] = param["growth_rate"]
        
        for t in range(stage["terms"]):
            term_result = {
                "term": term_counter,
                "parameters": []
            }
            
            for param_id, current_value in current_values.items():
                growth_rate = growth_rates.get(param_id, 0)
                
                new_value = (1 + growth_rate / 100) * current_value
                current_values[param_id] = new_value
                
                term_result["parameters"].append({
                    "parameter_id": ObjectId(param_id),
                    "value": round(new_value, 2),
                    "growth_rate": growth_rate
                })
            
            term_result["economic_health_score"] = calculate_economic_health(term_result["parameters"], city_profile)
            
            results.append(term_result)
            term_counter += 1
    
    ai_analysis = await generate_ai_analysis(snapshot, city_profile, results)
    
    update_result = await snapshots_collection.update_one(
        {"_id": ObjectId(snapshot_id)},
        {"$set": {
            "results": results,
            "ai_analysis": ai_analysis,
            "is_completed": True
        }}
    )
    
    updated_snapshot = await snapshots_collection.find_one({"_id": ObjectId(snapshot_id)})
    return serialize_mongo_doc(updated_snapshot)

@router.post("/{snapshot_id}/advance", response_model=Dict[str, Any])
async def advance_simulation(snapshot_id: str, advance: SimulationAdvance):
    snapshot = await snapshots_collection.find_one({"_id": ObjectId(snapshot_id)})
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    
    current_term = advance.current_term
    current_stage = None
    term_offset = 0
    
    for stage in snapshot["stages"]:
        if current_term <= term_offset + stage["terms"]:
            current_stage = stage
            break
        term_offset += stage["terms"]
    
    if not current_stage:
        raise HTTPException(400, "Simulation has reached its end")
    
    city_profile = await city_profiles_collection.find_one({"city_id": snapshot["city_id"]})
    if not city_profile:
        raise HTTPException(404, "City profile not found")
    
    current_values = {}
    if current_term > 1 and "results" in snapshot and len(snapshot["results"]) >= current_term - 1:
        prev_term_result = snapshot["results"][current_term - 2]
        for param in prev_term_result["parameters"]:
            current_values[str(param["parameter_id"])] = param["value"]
    else:
        for param in city_profile["parameters"]:
            current_values[str(param["parameter_id"])] = param["base_value"]
    
    growth_rates = {}
    for param in current_stage["parameters"]:
        growth_rates[str(param["parameter_id"])] = param["growth_rate"]
    
    term_result = {
        "term": current_term,
        "parameters": []
    }
    
    for param_id, current_value in current_values.items():
        growth_rate = growth_rates.get(param_id, 0)
        
        new_value = (1 + growth_rate / 100) * current_value
        
        term_result["parameters"].append({
            "parameter_id": ObjectId(param_id),
            "value": round(new_value, 2),
            "growth_rate": growth_rate
        })
    
    term_result["economic_health_score"] = calculate_economic_health(term_result["parameters"], city_profile)
    
    if "results" not in snapshot:
        snapshot["results"] = []
    
    if current_term <= len(snapshot["results"]):
        snapshot["results"][current_term - 1] = term_result
    else:
        snapshot["results"].append(term_result)
    
    total_terms = sum(stage["terms"] for stage in snapshot["stages"])
    is_completed = current_term >= total_terms
    
    if is_completed:
        ai_analysis = await generate_ai_analysis(snapshot, city_profile, snapshot["results"])
        update_fields = {
            "results": snapshot["results"],
            "is_completed": is_completed,
            "ai_analysis": ai_analysis
        }
    else:
        update_fields = {
            "results": snapshot["results"],
            "is_completed": is_completed
        }
    
    update_result = await snapshots_collection.update_one(
        {"_id": ObjectId(snapshot_id)},
        {"$set": update_fields}
    )
    
    updated_snapshot = await snapshots_collection.find_one({"_id": ObjectId(snapshot_id)})
    return serialize_mongo_doc(updated_snapshot)