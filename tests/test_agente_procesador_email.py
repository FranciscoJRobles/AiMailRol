import unittest
from types import SimpleNamespace
from ia.agentes.agente_procesador_email import AgenteProcesadorEmail
from ia.constantes.listas import INTENCIONES_EMAIL
import json

class TestAgenteProcesadorEmail(unittest.TestCase):
    def setUp(self):
        self.agente = AgenteProcesadorEmail()

    # def test_accion_simple(self):
    #     email = SimpleNamespace(body='Ataco al vampiro con mi espada.')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['accion'] for i in resultado['intenciones']))

    # def test_dialogo_pnj(self):
    #     email = SimpleNamespace(body='Le digo a guardia: No pienso abrir la puerta.')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['dialogo_pnj', 'dialogo'] for i in resultado['intenciones']))

    # def test_dialogo_pj(self):
    #     email = SimpleNamespace(body='Le digo a Juan: ¿Vamos juntos?')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['dialogo_pj', 'dialogo'] for i in resultado['intenciones']))

    # def test_estado_emocional(self):
    #     email = SimpleNamespace(body='Estoy nervioso y me tiemblan las manos.')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['estado_emocional'] for i in resultado['intenciones']))

    # def test_pensamiento(self):
    #     email = SimpleNamespace(body='Pienso que el mago nos está engañando.')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['pensamiento'] for i in resultado['intenciones']))

    # def test_meta(self):
    #     email = SimpleNamespace(body='Off: Esta semana estaré de viaje.')
    #     resultado = self.agente.analizar(email)
    #     self.assertTrue(any(i['tipo'] in ['meta', 'otro'] for i in resultado['intenciones']))
    #     self.assertTrue(resultado['meta']['es_meta_juego'])

    # def test_varias_intenciones(self):
    #     email = SimpleNamespace(body='Ataco al vampiro.\n\nLe digo a guardia: ¡No sé nada!\n\n¿Puedo ver si hay trampas?')
    #     resultado = self.agente.analizar(email)
    #     tipos = [i['tipo'] for i in resultado['intenciones']]
    #     self.assertTrue('accion' in tipos or 'otro' in tipos)
    #     self.assertTrue('dialogo_pnj' in tipos or 'dialogo' in tipos or 'otro' in tipos)
    #     self.assertTrue('consulta_narrador' in tipos or 'otro' in tipos)


    # def test_ia_integration(self):
    #     """
    #     Test de integración real con la IA (requiere conexión y credenciales).
    #     El resultado puede variar según el modelo, pero debe devolver al menos una intención reconocida.
    #     """
    #     email = SimpleNamespace(subject='', body='Me acerco al altar y le digo a Pedro: ¿Estás seguro de esto? Siento un escalofrío.')
    #     resultado = self.agente.analizar(email)
    #     print('\n--- Resultado IA ---')
    #     for idx, intencion in enumerate(resultado['intenciones']):
    #         print(f"Intención {idx+1}: [{intencion['tipo']}] -> {intencion['entidades']}")
    #     # Acepta cualquier intención válida definida en INTENCIONES_EMAIL
    #     self.assertTrue(any(i['tipo'] in INTENCIONES_EMAIL for i in resultado['intenciones']))
    #     # Opcional: comprueba que no haya tipos inesperados
    #     for i in resultado['intenciones']:
    #         self.assertIn(i['tipo'], INTENCIONES_EMAIL)
            
    def test_email_largo_desde_txt(self):
        with open('tests/emails/email_largo_ejemplo.txt', encoding='utf-8') as f:
            body = f.read()
        email = SimpleNamespace(body=body)
        lista_personajes_pj = [
            {'id': 1, 'nombre': 'Juan', 'tipo': 'pj'},
            {'id': 2, 'nombre': 'Darkcon', 'tipo': 'pnj'}
        ]
        resultado = self.agente.analizar(email, lista_personajes_pj)
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
        from ia.agentes.subagentes.subagente_clasificacion_critica_escena import SubagenteClasificacionCriticaEscenaEmailIA
        with open('tests/emails/email_clasificacion_dinamica.txt', encoding='utf-8') as f:
            body = f.read()
        email = SimpleNamespace(body=body)
        estado_actual = "narracion"
        subagente_critica = SubagenteClasificacionCriticaEscenaEmailIA()
        resultado = subagente_critica.analizar(email.body, estado_actual)
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
