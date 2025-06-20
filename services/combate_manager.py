# Maneja la lógica de emails de combate
from typing import Dict, List
from services.jugadores_manager import get_jugadores
import json
import os

COMBATES_PATH = os.path.join(os.path.dirname(__file__), '..', 'jsondata', 'combates.json')

class CombateManager:
    def __init__(self):
        self.combates = self._load_combates()  # {thread_id: {"rondas": [{"jugador": "mensaje", ...}], "ronda_actual": int, "participantes": [str, ...]}}

    def _load_combates(self):
        if os.path.exists(COMBATES_PATH):
            with open(COMBATES_PATH, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except Exception:
                    return {}
        return {}

    def _save_combates(self):
        with open(COMBATES_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.combates, f, ensure_ascii=False, indent=2)

    def add_participante(self, thread_id: str, remitente: str):
        if thread_id not in self.combates:
            self.combates[thread_id] = {"rondas": [{}], "ronda_actual": 0, "participantes": []}
        if remitente not in self.combates[thread_id]["participantes"]:
            self.combates[thread_id]["participantes"].append(remitente)
        self._save_combates()

    def add_mensaje(self, thread_id: str, remitente: str, mensaje: str):
        if thread_id not in self.combates:
            self.combates[thread_id] = {"rondas": [{}], "ronda_actual": 0, "participantes": []}
        ronda_actual = self.combates[thread_id]["ronda_actual"]
        rondas = self.combates[thread_id]["rondas"]
        # Asegura que la lista de rondas tenga la ronda actual
        while len(rondas) <= ronda_actual:
            rondas.append({})
        rondas[ronda_actual][remitente] = mensaje
        self._save_combates()

    def todos_han_respondido(self, thread_id: str) -> bool:
        if thread_id not in self.combates:
            return False
        jugadores = set(email.lower() for email in get_jugadores())
        ronda_actual = self.combates[thread_id]["ronda_actual"]
        respuestas = self.combates[thread_id]["rondas"][ronda_actual]
        remitentes = set()
        for k in respuestas.keys():
            # Extrae el email si hay alias (ej: 'Alias <email@dominio.com>')
            if '<' in k and '>' in k:
                email = k.split('<')[-1].split('>')[0].strip().lower()
            else:
                email = k.strip().lower()
            remitentes.add(email)
        return jugadores.issubset(remitentes)

    def avanzar_ronda(self, thread_id: str):
        if thread_id in self.combates:
            self.combates[thread_id]["ronda_actual"] += 1
            self.combates[thread_id]["rondas"].append({})
            self._save_combates()

    def get_mensajes_ronda(self, thread_id: str, ronda: int = None) -> Dict[str, str]:
        if thread_id not in self.combates:
            return {}
        if ronda is None:
            ronda = self.combates[thread_id]["ronda_actual"]
        rondas = self.combates[thread_id]["rondas"]
        if ronda < len(rondas):
            return rondas[ronda]
        return {}

    def reset(self, thread_id: str):
        if thread_id in self.combates:
            del self.combates[thread_id]
            self._save_combates()
        # Si no quedan combates, vacía el archivo
        if not self.combates:
            with open(COMBATES_PATH, 'w', encoding='utf-8') as f:
                f.write('{}')
