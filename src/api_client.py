import time
import requests
from typing import Dict, Any, Optional
from config import API_KEY, BASE_URL, REQUEST_DELAY, MAX_RETRIES, TIMEOUT

class APIClient:
    def __init__(self, logger):
        self.logger = logger
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': BASE_URL.replace('https://', '')
        }
        self.request_count = 0

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{BASE_URL}/{endpoint}"
        retries = 0
        
        while retries < MAX_RETRIES:
            try:
                self.logger.info(f"Requesting: {endpoint} | Params: {params}")
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=TIMEOUT
                )
                self.request_count += 1
                
                # Check for rate limiting or other errors
                if response.status_code == 200:
                    data = response.json()
                    if data.get('errors'):
                        self.logger.error(f"API Error: {data['errors']}")
                        return None
                    return data
                
                elif response.status_code == 429:
                    self.logger.warning("Rate limit reached (429). Waiting longer...")
                    time.sleep(60)
                
                else:
                    self.logger.error(f"HTTP Error {response.status_code}: {response.text}")
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Connection error: {e}")
            
            retries += 1
            self.logger.info(f"Retrying ({retries}/{MAX_RETRIES})...")
            time.sleep(REQUEST_DELAY * retries)
            
        return None
