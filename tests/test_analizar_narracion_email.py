import os
import unittest
from ia.langgraph.nodes.email_analysis_node import EmailAnalysisNode
import json
from utils.logger_config import configure_logging

# Configurar el logger
logger = configure_logging()

class TestAnalizarNarracionEmail(unittest.TestCase):
    def setUp(self):
        self.node = EmailAnalysisNode()

    def test_analizar_narracion_email(self):
        logger.info("Iniciando prueba: test_analizar_narracion_email")
        # Leer el contenido del email simulado
        with open('tests/emails/email_clasificacion_dinamica.txt', encoding='utf-8') as f:
            texto = f.read()

        logger.debug(f"Texto del email: {texto}")

        # Estado actual y lista de personajes simulados
        estado_actual = "narracion"
        lista_personajes_pj = [
            {'id': 1, 'nombre': 'Juan', 'tipo': 'pj'},
            {'id': 2, 'nombre': 'Darkcon', 'tipo': 'pnj'},
            {'id': 3, 'nombre': 'Pedro', 'tipo': 'pj'}
            
        ]

        logger.debug(f"Estado actual: {estado_actual}")
        logger.debug(f"Lista de personajes: {lista_personajes_pj}")

        # Llamar al método analizar_narracion_email
        resultado = self.node._analizar_narracion_email(
            texto=texto,
            estado_actual=estado_actual,
            lista_personajes_pj=lista_personajes_pj,
            personaje_sender='Darkcon'  # Simulando que Darkcon envía el email
        )

        logger.info("Prueba completada: test_analizar_narracion_email")
        logger.debug(f"Resultado del análisis: {json.dumps(resultado, indent=4, ensure_ascii=False)}")

        # Imprimir el resultado
        print('\n--- Resultado del análisis narrativo ---')
        print(json.dumps(resultado, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
