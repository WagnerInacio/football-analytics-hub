import sys
from pathlib import Path

# Adiciona raiz do projeto
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
from config import API_KEY, BASE_URL, LEAGUE_ID, SEASON, TIMEOUT

headers = {
    "x-apisports-key": API_KEY
}

url = f"{BASE_URL}/fixtures"

params = {
    "league": LEAGUE_ID,
    "season": SEASON
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=TIMEOUT
)

print(response.status_code)
print(response.json())