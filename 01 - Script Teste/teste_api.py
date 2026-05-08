import requests

API_KEY = "65b86e68bcf588309acb8b4f06730fee"

url = "https://v3.football.api-sports.io/status"

headers = {
    "x-apisports-key": API_KEY
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())
