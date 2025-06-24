import re


class AgenteProcesadorEmail:
    def analizar(self, email):
        """
        Analiza el email y extrae la intención y entidades principales.
        Retorna un diccionario con la estructura:
        {
            'intencion': str,  # p.ej. 'accion', 'consulta', 'respuesta', 'otro'
            'entidades': dict, # p.ej. {'accion': 'atacar', 'objetivo': 'vampiro'}
        }
        """
        body = email.body.lower() if hasattr(email, 'body') else ''
        subject = email.subject.lower() if hasattr(email, 'subject') else ''
        texto = subject + ' ' + body
        # Ejemplo simple: detección por palabras clave
        if any(palabra in texto for palabra in ['ataco', 'atacar', 'ataque']):
            return {'intencion': 'accion', 'entidades': {'accion': 'atacar'}}
        elif any(palabra in texto for palabra in ['estado', 'cómo estoy', 'mi vida']):
            return {'intencion': 'consulta', 'entidades': {'tipo': 'estado'}}
        elif any(palabra in texto for palabra in ['respondo', 'contesto']):
            return {'intencion': 'respuesta', 'entidades': {}}
        else:
            return {'intencion': 'otro', 'entidades': {}}
