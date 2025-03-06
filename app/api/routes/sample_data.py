from fastapi import APIRouter, HTTPException
from datetime import datetime
import random
from bson import ObjectId
from app.core.database import countries_collection, cities_collection, economic_parameters_collection, city_profiles_collection, snapshots_collection

router = APIRouter()

@router.post("/import-sample-data")
async def import_sample_data():
    try:
        # Clear existing data
        await countries_collection.delete_many({})
        await cities_collection.delete_many({})
        await economic_parameters_collection.delete_many({})
        await city_profiles_collection.delete_many({})
        await snapshots_collection.delete_many({})
        
        # Import sample countries
        countries = [
            {
                "name": "United States",
                "code": "US",
                "flag_url": "https://flagcdn.com/us.svg",
                "description": "The world's largest economy with diverse sectors including technology, finance, manufacturing, and services."
            },
            {
                "name": "United Kingdom",
                "code": "UK",
                "flag_url": "https://flagcdn.com/gb.svg",
                "description": "A highly developed economy focused on services, particularly finance, with strong international trade relations."
            }
        ]
        
        country_ids = {}
        for country in countries:
            result = await countries_collection.insert_one(country)
            country_ids[country["code"]] = result.inserted_id
        
        # Import sample cities
        cities = [
            {
                "name": "New York",
                "country_id": country_ids["US"],
                "description": "Global financial center and the most populous city in the US.",
                "population": 8804190,
                "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9"
            },
            {
                "name": "San Francisco",
                "country_id": country_ids["US"],
                "description": "Technology hub and cultural center on the west coast.",
                "population": 873965,
                "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29"
            },
            {
                "name": "London",
                "country_id": country_ids["UK"],
                "description": "Global city and financial hub with a diverse economy.",
                "population": 8982000,
                "image_url": "https://images.unsplash.com/photo-1505761671935-60b3a7427bad"
            }
        ]
        
        city_ids = {}
        for city in cities:
            result = await cities_collection.insert_one(city)
            city_ids[city["name"]] = result.inserted_id
        
        # Import sample economic parameters
        parameters = [
            {
                "name": "GDP Growth Rate",
                "code": "GDP",
                "unit": "%",
                "description": "Annual percentage growth rate of GDP",
                "category": "Growth"
            },
            {
                "name": "Unemployment Rate",
                "code": "UNEMP",
                "unit": "%",
                "description": "Percentage of labor force that is unemployed",
                "category": "Employment"
            },
            {
                "name": "Inflation Rate",
                "code": "INFL",
                "unit": "%",
                "description": "Annual percentage change in consumer prices",
                "category": "Monetary"
            },
            {
                "name": "Interest Rate",
                "code": "INT",
                "unit": "%",
                "description": "Central bank interest rate",
                "category": "Monetary"
            },
            {
                "name": "Foreign Investment",
                "code": "INVEST",
                "unit": "$ Billion",
                "description": "Annual foreign direct investment",
                "category": "Investment"
            },
            {
                "name": "Tax Revenue",
                "code": "TAX",
                "unit": "$ Billion",
                "description": "Annual tax revenue collected",
                "category": "Fiscal"
            },
            {
                "name": "Government Spending",
                "code": "SPEND",
                "unit": "$ Billion",
                "description": "Annual government expenditure",
                "category": "Fiscal"
            },
            {
                "name": "Budget Deficit",
                "code": "DEFICIT",
                "unit": "% of GDP",
                "description": "Government budget deficit as percentage of GDP",
                "category": "Fiscal"
            },
            {
                "name": "Housing Price Index",
                "code": "HOUSE",
                "unit": "Index",
                "description": "Housing price index (base year = 100)",
                "category": "Real Estate"
            },
            {
                "name": "Stock Market Index",
                "code": "STOCK",
                "unit": "Index",
                "description": "Main stock market index",
                "category": "Financial"
            }
        ]
        
        parameter_ids = {}
        for param in parameters:
            result = await economic_parameters_collection.insert_one(param)
            parameter_ids[param["code"]] = result.inserted_id
        
        # Create city profiles with historical data
        for city_name, city_id in city_ids.items():
            # Different base values for each city
            if city_name == "New York":
                base_values = {
                    "GDP": 2.8,
                    "UNEMP": 5.2,
                    "INFL": 2.1,
                    "INT": 3.5,
                    "INVEST": 120.5,
                    "TAX": 85.3,
                    "SPEND": 92.1,
                    "DEFICIT": 3.2,
                    "HOUSE": 180.5,
                    "STOCK": 3500.0
                }
            elif city_name == "San Francisco":
                base_values = {
                    "GDP": 3.5,
                    "UNEMP": 4.2,
                    "INFL": 2.5,
                    "INT": 3.5,
                    "INVEST": 95.2,
                    "TAX": 68.7,
                    "SPEND": 72.1,
                    "DEFICIT": 2.8,
                    "HOUSE": 220.5,
                    "STOCK": 3800.0
                }
            else:  # London
                base_values = {
                    "GDP": 2.2,
                    "UNEMP": 4.8,
                    "INFL": 2.3,
                    "INT": 2.5,
                    "INVEST": 85.3,
                    "TAX": 75.6,
                    "SPEND": 82.4,
                    "DEFICIT": 3.5,
                    "HOUSE": 165.8,
                    "STOCK": 3200.0
                }
                
            # Create parameter list with historical data
            city_parameters = []
            for code, param_id in parameter_ids.items():
                base_value = base_values[code]
                
                # Generate historical values (12 months)
                historical_values = []
                current_value = base_value
                for month in range(12, 0, -1):
                    # Random growth rate between -2% and 5%
                    growth_rate = random.uniform(-2, 5)
                    
                    if month == 12:
                        # First historical month uses the base value
                        value = current_value
                    else:
                        # Apply reverse growth to go backwards in time
                        value = current_value / (1 + growth_rate / 100)
                        current_value = value
                    
                    historical_values.append({
                        "term": 13 - month,  # Term 1 is oldest, Term 12 is newest
                        "value": round(value, 2),
                        "growth_rate": round(growth_rate, 2),
                        "date": f"2023-{month:02d}-01"  # Mock dates for 2023
                    })
                
                # Default growth rate varies by parameter type
                if code in ["GDP", "INVEST", "TAX", "STOCK", "HOUSE"]:
                    default_growth_rate = 2.5  # Usually positive for these
                elif code in ["UNEMP", "INFL", "DEFICIT"]:
                    default_growth_rate = -0.5  # Usually want these to decrease
                else:
                    default_growth_rate = 1.0  # Neutral
                
                city_parameters.append({
                    "parameter_id": param_id,
                    "base_value": base_value,
                    "historical_values": historical_values,
                    "default_growth_rate": default_growth_rate
                })
            
            # Calculate economic health score
            economic_health = 50 + random.uniform(-10, 10)
            
            # Create summary
            if city_name == "New York":
                summary = "New York's economy shows strong growth in financial services and real estate, with moderate inflation and decreasing unemployment."
            elif city_name == "San Francisco":
                summary = "San Francisco's economy is driven by technology sector growth, with high housing costs and relatively low unemployment."
            else:  # London
                summary = "London's economy features strong service sector performance, moderate inflation, and steady foreign investment despite economic challenges."
            
            # Create the city profile
            city_profile = {
                "city_id": city_id,
                "last_updated": datetime.now(),
                "parameters": city_parameters,
                "economic_health_score": economic_health,
                "summary": summary
            }
            
            await city_profiles_collection.insert_one(city_profile)
        
        # Create a sample snapshot for New York
        ny_snapshot = {
            "name": "NYC Growth Plan 2024",
            "city_id": city_ids["New York"],
            "created_at": datetime.now(),
            "stages": [
                {
                    "stage_number": 1,
                    "terms": 6,
                    "parameters": [
                        {
                            "parameter_id": parameter_ids["GDP"],
                            "growth_rate": 3.5
                        },
                        {
                            "parameter_id": parameter_ids["UNEMP"],
                            "growth_rate": -1.2
                        },
                        {
                            "parameter_id": parameter_ids["INVEST"],
                            "growth_rate": 4.0
                        }
                    ]
                },
                {
                    "stage_number": 2,
                    "terms": 6,
                    "parameters": [
                        {
                            "parameter_id": parameter_ids["GDP"],
                            "growth_rate": 2.8
                        },
                        {
                            "parameter_id": parameter_ids["UNEMP"],
                            "growth_rate": -0.8
                        },
                        {
                            "parameter_id": parameter_ids["INVEST"],
                            "growth_rate": 3.0
                        }
                    ]
                }
            ],
            "results": [],
            "is_completed": False
        }
        
        await snapshots_collection.insert_one(ny_snapshot)
        
        return {
            "message": "Sample data imported successfully",
            "details": {
                "countries": len(countries),
                "cities": len(cities),
                "parameters": len(parameters),
                "city_profiles": len(city_ids),
                "snapshots": 1
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Error importing sample data: {str(e)}")