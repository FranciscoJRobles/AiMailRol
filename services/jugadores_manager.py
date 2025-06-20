# Manager para cargar la lista de jugadores desde un archivo JSON
import json
import os

JUGADORES_PATH = os.path.join(os.path.dirname(__file__), '..', 'jsondata', 'jugadores.json')

def get_jugadores() -> list:
    with open(JUGADORES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
