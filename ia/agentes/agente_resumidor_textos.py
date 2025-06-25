class AgenteResumidorTextos:
    def __init__(self, ia_client):
        self.ia_client = ia_client

    def resumir_textos(self, lista_textos, contexto_extra=None):
        """
        Recibe una lista de textos y opcionalmente contexto extra, y devuelve un resumen generado por la IA.
        """
        prompt = (
            "Eres un agente experto en resumir mensajes de rol. Recibe una lista de mensajes y genera un resumen claro y coherente que recoja los eventos, acciones y diálogos más relevantes. "
        )
        if contexto_extra:
            prompt += f"\nContexto adicional: {contexto_extra}"
        prompt += "\nMensajes a resumir:\n" + "\n".join(lista_textos)
        # Llama a la IA (debes pasarle el prompt y obtener el resumen)
        resumen = self.ia_client.procesar_mensaje(prompt)
        return resumen
