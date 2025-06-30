import unittest
from ia.agentes.subagentes.subagente_analisis_email import SubagenteAnalisisEmailIA
import json
import logging

class TestAnalizarNarracionEmail(unittest.TestCase):
    def setUp(self):
        # Configurar logging para respuestas inválidas
        logging.basicConfig(
            filename='invalid_responses.log',
            level=logging.ERROR,
            format='%(asctime)s - %(message)s'
        )
        self.subagente = SubagenteAnalisisEmailIA()

    def test_analizar_narracion_email(self):
        # Leer el contenido del email simulado
        with open('tests/emails/email_clasificacion_dinamica.txt', encoding='utf-8') as f:
            texto = f.read()

        # Estado actual y lista de personajes simulados
        estado_actual = "narracion"
        lista_personajes_pj = [
            {'id': 1, 'nombre': 'Juan', 'tipo': 'pj'},
            {'id': 2, 'nombre': 'Darkcon', 'tipo': 'pnj'},
            {'id': 3, 'nombre': 'Pedro', 'tipo': 'pj'}
            
        ]

        # Llamar al método analizar_narracion_email
        resultado = self.subagente.analizar_narracion_email(
            texto=texto,
            estado_actual=estado_actual,
            lista_personajes_pj=lista_personajes_pj,
            personaje_sender='Darkcon'  # Simulando que Darkcon envía el email
        )

        # Imprimir el resultado
        print('\n--- Resultado del análisis narrativo ---')
        print(json.dumps(resultado, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
