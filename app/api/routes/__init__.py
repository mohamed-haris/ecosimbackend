from fastapi import APIRouter
from app.api.routes import countries, cities, parameters, city_profiles, snapshots, sample_data

router = APIRouter()

router.include_router(countries.router, prefix="/countries", tags=["countries"])
router.include_router(cities.router, prefix="/cities", tags=["cities"])
router.include_router(parameters.router, prefix="/parameters", tags=["parameters"])
router.include_router(city_profiles.router, prefix="/city-profiles", tags=["city profiles"])
router.include_router(snapshots.router, prefix="/snapshots", tags=["snapshots"])
router.include_router(sample_data.router, prefix="/import", tags=["sample data"])