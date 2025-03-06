from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CountryCreate(BaseModel):
    name: str
    code: str
    flag_url: Optional[str] = None
    description: Optional[str] = None

class CityCreate(BaseModel):
    name: str
    country_id: str
    description: Optional[str] = None
    population: Optional[int] = None
    image_url: Optional[str] = None

class EconomicParameterCreate(BaseModel):
    name: str
    code: str
    unit: str
    description: Optional[str] = None
    category: str

class ParameterValue(BaseModel):
    parameter_id: str
    base_value: float
    default_growth_rate: float
    historical_values: Optional[List[Dict[str, Any]]] = []

class CityProfileCreate(BaseModel):
    city_id: str
    parameters: List[ParameterValue]
    economic_health_score: Optional[float] = 50.0
    summary: Optional[str] = None

class SimulationStage(BaseModel):
    stage_number: int
    terms: int
    parameters: List[Dict[str, Any]]

class SnapshotCreate(BaseModel):
    name: str
    city_id: str
    stages: List[SimulationStage]

class SimulationAdvance(BaseModel):
    current_term: int