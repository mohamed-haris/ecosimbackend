from bson import ObjectId

def serialize_mongo_doc(doc):
    """Recursively convert all ObjectIds to strings in a MongoDB document."""
    if doc is None:
        return None
    
    result = {}
    for key, value in doc.items():
        if key == '_id':
            result['id'] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, list):
            result[key] = [serialize_mongo_doc(item) if isinstance(item, dict) 
                          else str(item) if isinstance(item, ObjectId)
                          else item for item in value]
        elif isinstance(value, dict):
            result[key] = serialize_mongo_doc(value)
        else:
            result[key] = value
    
    return result