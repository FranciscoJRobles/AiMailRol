from ia.agentes.subagentes.subagente_recopilador_contexto import SubagenteRecopiladorContexto
from ia.agentes.subagentes.subagente_resumidor_textos import SubagenteResumidorTextos

class AgenteContextoHistoria:
    def __init__(self, db, ia_client):
        self.db = db
        self.resumidor_textos = SubagenteResumidorTextos(ia_client)
        self.recopilador_contexto = SubagenteRecopiladorContexto(db, self.resumidor_textos)

    def obtener_contexto_para_ia(self, scene_id, campaign_id=None, max_emails=10, n_puros=3):
        """
        Devuelve el contexto estructurado para la IA: instrucciones de sistema y narrativa/historial.
        """
        # 1. Recopilar contexto narrativo y resúmenes
        contexto = self.recopilador_contexto.recopilar_resumenes_contexto(scene_id, max_emails, n_puros)
        # 2. Recuperar ambientación/directrices de campaña
        if campaign_id:
            ambientacion = self.recopilador_contexto.obtener_contexto_ambientacion(campaign_id)
        else:
            ambientacion = None
        # 3. Construir la estructura para la IA
        sistema = []
        if ambientacion:
            sistema.append(ambientacion)
        if 'campaign' in contexto:
            sistema.append(f"Resumen campaña: {contexto['campaign'].get('resumen','')}")
        if 'story_state' in contexto:
            sistema.append(f"Resumen estado historia: {contexto['story_state'].get('contenido_resumido','')}")
        if 'scene' in contexto:
            sistema.append(f"Resumen escena: {contexto['scene'].get('resumen_estado','')}")
        # 4. Historial narrativo: emails recientes y/o resumen final de la escena
        historial = []
        if contexto.get('emails_puros'):
            historial.extend(contexto['emails_puros'])
        if contexto.get('resumen_final'):
            historial.append(contexto['resumen_final'])
        # 5. Devolver estructura lista para procesar_mensaje
        return {
            "sistema": "\n".join([s for s in sistema if s]),
            "historial": historial
        }

    def obtener_contexto(self):
        # Aquí se puede implementar la lógica para obtener el contexto de la historia
        return self.historia

    def actualizar_historia(self, nueva_historia):
        self.historia = nueva_historia
        return self.historia

    def __str__(self):
        return f"AgenteContextoHistoria(historia={self.historia})"