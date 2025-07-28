# utils/db_location_validator.py
import requests
import os

def get_locationqr_by_id(location_id: int):
    """
    Get location QR by location id for location validation purpose at return book stage.
    Returns (is_successful: bool, message: str)
    """
    base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    try:
        response = requests.get(f"{base_url}/api/v1/metadata/locations/{location_id}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)
    
    