import requests

API_KEY = "65b86e68bcf588309acb8b4f06730fee"

headers = {
    "x-apisports-key": API_KEY
}

url = "https://v3.football.api-sports.io/fixtures"

params = {
    "league": 71,
    "season": 2024
}

response = requests.get(url, headers=headers, params=params)

print(response.status_code)
print(response.json())