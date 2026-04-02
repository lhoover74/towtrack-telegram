import requests
from bot.config import API_URL


def create_vehicle(payload: dict):
    response = requests.post(f"{API_URL}/vehicles/", json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def search_vehicle(plate: str):
    response = requests.get(f"{API_URL}/vehicles/{plate}", timeout=15)
    response.raise_for_status()
    return response.json()
