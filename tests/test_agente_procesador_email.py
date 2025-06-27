import unittest
from types import SimpleNamespace
from ia.agentes.agente_email import AgenteAnalizadorEmail
from ia.agentes.subagentes.subagente_analisis_email import SubagenteAnalisisEmailIA
import json

class TestAgenteProcesadorEmail(unittest.TestCase):
    def setUp(self):
        self.agente = AgenteAnalizadorEmail()
            
    def test_email_largo_desde_txt(self):
        with open('tests/emails/email_largo_ejemplo.txt', encoding='utf-8') as f:
            body = f.read()
        email = SimpleNamespace(body=body)
        lista_personajes_pj = [
            {'id': 1, 'nombre': 'Juan', 'tipo': 'pj'},
            {'id': 2, 'nombre': 'Darkcon', 'tipo': 'pnj'}
        ]
        resultado = SubagenteAnalisisEmailIA().clasificar(email, lista_personajes_pj)
        print('\n--- Resultado estructurado de la IA ---')
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
        # Si quieres ver solo las intenciones de forma más visual:
        print('\n--- Intenciones detalladas ---')
        for idx, intencion in enumerate(resultado.get('intenciones', [])):
            print(f"Bloque {idx+1}:")
            for k, v in intencion.items():
                print(f"  {k}: {v}")
            print('-' * 40)
        # Si existe metajuego, mostrarlo también
        if 'metajuego' in resultado:
            print('\n--- Meta-juego detectado ---')
            print(json.dumps(resultado['metajuego'], indent=4, ensure_ascii=False))
        # Asserts opcionales aquí

    def test_critica_escena_cambio_estado(self):
        with open('tests/emails/email_clasificacion_dinamica.txt', encoding='utf-8') as f:
            body = f.read()
        email = SimpleNamespace(body=body)
        estado_actual = "narracion"
        resultado = SubagenteAnalisisEmailIA().analizarTransicion(email.body, estado_actual)
        print('\n--- Resultado crítica de escena ---')
        import json
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
        if resultado and isinstance(resultado, dict):
            if resultado.get('cambio_detectado'):
                print(f"Cambio de estado detectado: Sí. Nuevo estado: {resultado.get('nuevo_estado')}")
            else:
                print("No se ha detectado cambio de estado.")
        else:
            print("No se pudo analizar el cambio de estado.")
        # Assert opcional para comprobar que detecta el cambio
        # self.assertTrue(resultado.get('cambio_detectado'))

if __name__ == '__main__':
    unittest.main()
