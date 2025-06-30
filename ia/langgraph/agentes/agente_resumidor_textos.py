class SubagenteResumidorTextos:
    def __init__(self, ia_client):
        self.ia_client = ia_client

    def resumir_emails(self, resumen_previo_scene, emails_nuevos, contexto_extra=None):
        """
        Fusiona el resumen previo de la escena con los emails recientes, generando un nuevo resumen coherente y sintético.
        """
        instrucciones = (
            "Eres un agente experto en resumir mensajes de una partida de rol. Fusiona el resumen previo de la escena con los mensajes recientes. "
            "Mantén lo relevante del resumen previo y añade los eventos, acciones y diálogos más importantes de los mensajes nuevos. "
            "El nuevo resumen debe ser claro, coherente y no crecer indefinidamente: sintetiza la nueva información con la vieja, eliminando detalles redundantes o irrelevantes."
        )
        if contexto_extra:
            instrucciones += f"\nContexto adicional: {contexto_extra}"
        historial = []
        if resumen_previo_scene:
            historial.append(f"Resumen previo de la escena:\n{resumen_previo_scene}")
        if emails_nuevos:
            historial.extend(emails_nuevos)
        mensaje_principal = "Fusiona el resumen previo y los mensajes recientes en un único resumen sintético."
        contexto = {"sistema": instrucciones, "historial": historial}
        resumen = self.ia_client.procesar_mensaje(mensaje_principal, contexto=contexto, perfil="resumen")
        return resumen

    def resumir_resumenes(self, resumen_superior, lista_resumenes, contexto_extra=None):
        """
        Fusiona varios resúmenes (por ejemplo, de escenas o story_states) en un resumen superior (story_state o campaign).
        """
        instrucciones = (
            "Eres un agente experto en sintetizar resúmenes de partidas de rol. Fusiona el resumen superior previo con los resúmenes parciales. "
            "Mantén lo relevante del resumen superior y añade los eventos, acciones y cambios importantes de los resúmenes parciales. "
            "El nuevo resumen debe ser claro, coherente y no crecer indefinidamente: sintetiza la nueva información con la vieja, eliminando detalles redundantes o irrelevantes."
        )
        if contexto_extra:
            instrucciones += f"\nContexto adicional: {contexto_extra}"
        historial = []
        if resumen_superior:
            historial.append(f"Resumen superior previo:\n{resumen_superior}")
        if lista_resumenes:
            historial.extend(lista_resumenes)
        mensaje_principal = "Fusiona el resumen superior previo y los resúmenes parciales en un único resumen sintético."
        contexto = {"sistema": instrucciones, "historial": historial}
        resumen = self.ia_client.procesar_mensaje(mensaje_principal, contexto=contexto, perfil="resumen")
        return resumen