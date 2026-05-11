import sys
from pathlib import Path

# Adiciona raiz do projeto
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
from config import API_KEY, BASE_URL

url = f"{BASE_URL}/status"

headers = {
    "x-apisports-key": API_KEY
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())