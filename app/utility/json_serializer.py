import json
import uuid
import datetime
import logging
from typing import Any, Dict, List, Optional, Union, Tuple

class CalderaJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for Caldera objects.
    
    This encoder handles special types like datetime, UUID, and custom Caldera objects.
    """
    
    def default(self, obj: Any) -> Any:
        """
        Convert objects to JSON serializable types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON serializable representation of the object
        """
        # Handle datetime objects
        if isinstance(obj, datetime.datetime):
            return {
                "__type__": "datetime",
                "value": obj.isoformat()
            }
            
        # Handle UUID objects
        if isinstance(obj, uuid.UUID):
            return {
                "__type__": "uuid",
                "value": str(obj)
            }
            
        # Handle set objects
        if isinstance(obj, set):
            return {
                "__type__": "set",
                "value": list(obj)
            }
            
        # Handle bytes objects
        if isinstance(obj, bytes):
            return {
                "__type__": "bytes",
                "value": obj.decode('utf-8', errors='replace')
            }
            
        # Handle Caldera objects with to_json method
        if hasattr(obj, 'to_json'):
            return obj.to_json()
            
        # Handle Caldera objects with schema method
        if hasattr(obj, 'schema'):
            return {
                "__type__": obj.__class__.__name__,
                "value": obj.schema()
            }
            
        # Default behavior
        return super().default(obj)


class CalderaJSONDecoder(json.JSONDecoder):
    """
    Custom JSON decoder for Caldera objects.
    
    This decoder handles special types encoded by CalderaJSONEncoder.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the decoder with object_hook."""
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        self.logger = logging.getLogger('json_decoder')
        
    def object_hook(self, obj: Dict[str, Any]) -> Any:
        """
        Convert JSON objects back to Python objects.
        
        Args:
            obj: JSON object to deserialize
            
        Returns:
            Python object
        """
        # Check if this is a special type
        if "__type__" in obj:
            obj_type = obj["__type__"]
            value = obj["value"]
            
            # Handle datetime
            if obj_type == "datetime":
                try:
                    return datetime.datetime.fromisoformat(value)
                except ValueError:
                    self.logger.warning(f"Failed to parse datetime: {value}")
                    return value
                    
            # Handle UUID
            if obj_type == "uuid":
                try:
                    return uuid.UUID(value)
                except ValueError:
                    self.logger.warning(f"Failed to parse UUID: {value}")
                    return value
                    
            # Handle set
            if obj_type == "set":
                return set(value)
                
            # Handle bytes
            if obj_type == "bytes":
                return value.encode('utf-8')
                
            # For other types, return as is for now
            # In a full implementation, we would need to import and instantiate
            # the appropriate class based on obj_type
            return obj
            
        # Return as is if not a special type
        return obj


def serialize_object(obj: Any) -> str:
    """
    Serialize an object to JSON.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    return json.dumps(obj, cls=CalderaJSONEncoder)


def deserialize_object(json_str: str) -> Any:
    """
    Deserialize a JSON string to an object.
    
    Args:
        json_str: JSON string to deserialize
        
    Returns:
        Deserialized object
    """
    return json.loads(json_str, cls=CalderaJSONDecoder)


def serialize_to_file(obj: Any, file_path: str) -> None:
    """
    Serialize an object to a JSON file.
    
    Args:
        obj: Object to serialize
        file_path: Path to save the JSON file
    """
    with open(file_path, 'w') as f:
        json.dump(obj, f, cls=CalderaJSONEncoder, indent=2)


def deserialize_from_file(file_path: str) -> Any:
    """
    Deserialize an object from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Deserialized object
    """
    with open(file_path, 'r') as f:
        return json.load(f, cls=CalderaJSONDecoder)
