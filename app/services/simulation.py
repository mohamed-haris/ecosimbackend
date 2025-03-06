from app.core.database import city_profiles_collection, economic_parameters_collection
from bson import ObjectId

def calculate_economic_health(parameters, city_profile):
    total_weight = 0
    weighted_sum = 0
    
    for param in parameters:
        param_id = str(param["parameter_id"])
        param_value = param["value"]
        
        base_value = None
        for base_param in city_profile["parameters"]:
            if str(base_param["parameter_id"]) == param_id:
                base_value = base_param["base_value"]
                break
        
        if base_value is None or base_value == 0:
            continue
        
        relative_change = (param_value / base_value) - 1
        
        weight = 1
        total_weight += weight
        
        if param_id.endswith("GDP") or param_id.endswith("INVEST"):
            factor = 1 if relative_change > 0 else -1
        elif param_id.endswith("UNEMP") or param_id.endswith("INFL"):
            factor = -1 if relative_change > 0 else 1
        else:
            factor = 1 if relative_change > 0 else -1
        
        weighted_sum += factor * weight * abs(relative_change) * 50
    
    if total_weight == 0:
        return 50 
    
    health_score = 50 + (weighted_sum / total_weight)
    
    return max(0, min(100, health_score))