import json
import openai
from bson import ObjectId
from app.core.config import OPENAI_API_KEY
from app.core.database import economic_parameters_collection

client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def generate_ai_analysis(snapshot, city_profile, results):
    try:
        parameter_details = {}
        for param in city_profile["parameters"]:
            param_id = str(param["parameter_id"])
            parameter = await economic_parameters_collection.find_one({"_id": param["parameter_id"]})
            if parameter:
                parameter_details[param_id] = {
                    "name": parameter["name"],
                    "unit": parameter["unit"],
                    "category": parameter["category"],
                    "base_value": param["base_value"]
                }
        
        first_term = results[0] if results else None
        last_term = results[-1] if results else None
        
        if not first_term or not last_term:
            return {
                "summary": "Insufficient data for analysis",
                "impacts": [],
                "recommendations": "Complete the simulation to get recommendations",
                "comparison_to_default": "No simulation data available"
            }
        
        parameter_changes = []
        for param in last_term["parameters"]:
            param_id = str(param["parameter_id"])
            if param_id in parameter_details:
                param_detail = parameter_details[param_id]
                base_value = param_detail["base_value"]
                final_value = param["value"]
                
                parameter_changes.append({
                    "name": param_detail["name"],
                    "base_value": f"{base_value} {param_detail['unit']}",
                    "final_value": f"{final_value} {param_detail['unit']}",
                    "percent_change": f"{((final_value / base_value) - 1) * 100:.2f}%"
                })
        
        prompt = f"""
You are an expert economic analyst. Analyze the following economic simulation results and provide insights:

City: {snapshot['name']}
Simulation length: {len(results)} terms

Parameter Changes (Base → Final):
{json.dumps(parameter_changes, indent=2)}

Initial Economic Health Score: {first_term['economic_health_score']:.2f}
Final Economic Health Score: {last_term['economic_health_score']:.2f}

Please provide:
1. A summary of the overall economic impact (2-3 paragraphs)
2. Specific impacts for each parameter (one sentence per parameter)
3. Policy recommendations based on these results (2-3 bullet points)
4. A comparison to the default economic trajectory

Format your response as JSON with the following structure:
{{
  "summary": "overall economic impact analysis",
  "impacts": [
    {{
      "parameter": "parameter name",
      "impact": "description of impact"
    }}
  ],
  "recommendations": "bullet point policy recommendations",
  "comparison_to_default": "how this differs from default trajectory"
}}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert economic analyst providing JSON-formatted insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        impacts_with_ids = []
        for impact in analysis.get("impacts", []):
            param_name = impact.get("parameter", "")
            param_id = None
            
            for pid, details in parameter_details.items():
                if details["name"].lower() == param_name.lower():
                    param_id = pid
                    break
            
            if param_id:
                impacts_with_ids.append({
                    "parameter_id": ObjectId(param_id),
                    "impact": impact["impact"]
                })
            else:
                impacts_with_ids.append({
                    "parameter_id": None,
                    "impact": impact["impact"]
                })
        
        analysis["impacts"] = impacts_with_ids
        return analysis
    
    except Exception as e:
        print(f"Error generating AI analysis: {str(e)}")
        return {
            "summary": "Analysis temporarily unavailable",
            "impacts": [],
            "recommendations": "Please try again later",
            "comparison_to_default": "Error generating analysis"
        }