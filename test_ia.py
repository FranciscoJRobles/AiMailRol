# test_ia.py
from ia.ia_client import IAClient

if __name__ == "__main__":
    ia = IAClient()
    pregunta = "¿Cuál es la capital de Francia?"
    respuesta = ia.procesar_mensaje(pregunta)
    print("Respuesta IA:", respuesta)