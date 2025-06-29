from ia.agentes.subagentes.subagente_gestor_emails import SubagenteGestorEmails
from sqlalchemy.orm import Session
from api.models.scene import Scene
from api.models.story_state import StoryState
from api.models.campaign import Campaign
from api.models.ruleset import Ruleset
from api.models.character import Character

class SubagenteRecopiladorContexto:
    def __init__(self, db: Session, resumidor_textos=None):
        self.db = db
        self.gestor_emails = SubagenteGestorEmails(db)
        self.resumidor_textos = resumidor_textos  # Puede ser None si no usas IA para resumir

    def recopilar_resumenes_contexto(self, scene_id, max_emails=10, n_puros=3):
        contexto = {}
        # 1. Emails recientes o resumen
        bodies_a_resumir, bodies_puros, emails_a_resumir, emails_puros, hay_que_resumir = self.gestor_emails.gestionar_emails_para_contexto(scene_id, max_emails, n_puros)
        contexto['emails_puros'] = bodies_puros
        # Solo usamos bodies_a_resumir y hay_que_resumir como variables locales
        # 2. Escena
        scene = get_scene_by_id(self.db, scene_id)
        resumen_final = scene.resumen_estado if scene else ''
        if hay_que_resumir and bodies_a_resumir and self.resumidor_textos:
            # Generar resumen de los emails antiguos y combinarlo con el resumen existente
            resumen_emails = self.resumidor_textos.resumir_textos(bodies_a_resumir, contexto_extra=resumen_final)
            resumen_final = resumen_emails  # O combinar ambos como prefieras
            # Marcar emails como procesados
            self.gestor_emails.marcar_emails_como_procesados(emails_a_resumir)
        contexto['resumen_final'] = resumen_final
        if scene:
            contexto['scene'] = {
                'titulo': scene.titulo,
                'resumen_estado': scene.resumen_estado,
                'descripcion_larga': scene.descripcion_larga,
                'activa': scene.activa
            }
            # 3. StoryState
            story_state = get_story_state_by_id(self.db, scene.story_state_id) if scene.story_state_id else None
            if story_state:
                contexto['story_state'] = {
                    'nombre': story_state.nombre,
                    'descripcion': story_state.descripcion,
                    'contenido_resumido': story_state.contenido_resumido,
                    'activa': story_state.activa
                }
                # 4. Campaign
                campaign = get_campaign_by_id(self.db, story_state.campaign_id) if story_state.campaign_id else None
                if campaign:
                    contexto['campaign'] = {
                        'nombre': campaign.nombre,
                        'descripcion': campaign.descripcion,
                        'resumen': campaign.resumen,
                        'activa': campaign.activa
                    }
            # 5. Personajes involucrados en la escena
            personajes = get_personajes_por_escena(self.db, scene_id)
            contexto['personajes'] = []
            for personaje in personajes:
                contexto['personajes'].append({
                    'nombre': personaje.nombre,
                    'ficha': personaje.ficha_json if hasattr(personaje, 'ficha_json') else {},
                    'estado_actual': personaje.estado_actual_json if hasattr(personaje, 'estado_actual_json') else {}
                })
        return contexto

    def obtener_contexto_ambientacion(self, campaign_id):
        """
        Recupera y devuelve el contexto de ambientación y directrices desde ruleset.contexto_json para la campaña dada.
        """
        ruleset = self.db.query(Ruleset).filter(Ruleset.campaign_id == campaign_id, Ruleset.activo == True).first()
        if ruleset and ruleset.contexto_json:
            return ruleset.contexto_json
        return {}

    def ensamblar_contexto_para_ia(self, scene_id, max_emails=10, n_puros=3):
        """
        Ensambla el contexto final para la IA, clasificando el contexto de ambientación como SystemMessage
        y el resto de resúmenes y datos como HumanMessage.
        Devuelve una lista de mensajes tipo [{role: 'system', content: ...}, {role: 'user', content: ...}]
        """
        # 1. Recopilar resúmenes y contexto dinámico
        contexto = self.recopilar_resumenes_contexto(scene_id, max_emails, n_puros)
        # 2. Obtener campaign_id
        campaign_id = None
        if 'scene' in contexto and 'story_state' in contexto:
            campaign_id = contexto['story_state'].get('campaign_id')
        elif 'campaign' in contexto:
            campaign_id = contexto['campaign'].get('id')
        # 3. Obtener contexto de ambientación
        contexto_ambientacion = self.obtener_contexto_ambientacion(campaign_id) if campaign_id else {}
        # 4. Preparar mensajes
        mensajes = []
        if contexto_ambientacion:
            mensajes.append({"role": "system", "content": contexto_ambientacion})
        # El resto del contexto (resúmenes, emails, etc.) como HumanMessage
        mensajes.append({"role": "user", "content": contexto})
        return mensajes
