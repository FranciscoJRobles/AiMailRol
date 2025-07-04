from sqlalchemy.orm import Session
from api.models.scene import Scene
from api.models.story import Story
from api.models.campaign import Campaign
from api.models.ruleset import Ruleset
from api.models.character import Character
from api.managers.story_manager import StoryManager
from api.managers.scene_manager import SceneManager
from api.managers.email_manager import EmailManager
from api.managers.campaign_manager import CampaignManager
from api.managers.character_manager import CharacterManager
from api.managers.ruleset_manager import RulesetManager

class ContextCollectorChain:
    def __init__(self, db: Session, resumidor_textos=None):
        self.db = db
        self.resumidor_textos = resumidor_textos  # Puede ser None si no usas IA para resumir

    def gestionar_emails_para_contexto(self, scene_id, max_emails=10, n_puros=3):
        """
        Si hay menos de max_emails emails no procesados, devuelve sus bodies.
        Si hay max_emails o más, resume los más antiguos y deja los n_puros últimos como contexto puro.
        Devuelve: (emails_a_resumir, emails_puros, emails_objetos_a_resumir, emails_objetos_puros, hay_que_resumir)
        """
        emails = EmailManager.get_emails_processed_not_sumarized_by_scene_id(self.db, scene_id)
        if len(emails) >= max_emails:
            emails_a_resumir = emails[:-n_puros]
            emails_puros = emails[-n_puros:]
            bodies_a_resumir = [email.body for email in emails_a_resumir]
            bodies_puros = [email.body for email in emails_puros]
            EmailManager.mark_emails_as_sumarized(self.db, emails_a_resumir)            
            return bodies_a_resumir, bodies_puros
        else:
            bodies = [email.body for email in emails]
            return [], bodies

    def recopilar_resumenes_contexto(self, scene_id, max_scenes=5, scenes_puros=2):
        """
        Recopila los resúmenes de Campaign, Story y Scene en un dict estructurado.
        Devuelve un dict con el orden lógico: Resumen de Campaign, Resumen de Story, Lista de resúmenes de Scene.
        """
        contexto = {
            "campaign_resumen": None,
            "story_resumen": None,
            "scenes_resumenes": []
        }

        # 1. Obtener la escena actual
        scene = SceneManager.get_scene_by_id(self.db, scene_id)
        if not scene:
            return contexto  # Si no hay escena, devolvemos el contexto vacío

        # 2. Obtener la historia asociada a la escena
        story = StoryManager.get_story_by_id(self.db, scene.story_id) if scene.story_id else None
        if story:
            story_resumen = story.resumen

            # 3. Obtener la campaña asociada a la historia
            campaign = CampaignManager.get_campaign(self.db, story.campaign_id) if story.campaign_id else None
            if campaign:
                campaign_resumen = campaign.resumen

        # 4. Recopilar resúmenes de todas las escenas asociadas a la historia
        if story:
            scenes = SceneManager.get_not_summarized_scenes_by_story_id(self.db, story.id)
            if len(scenes) >= max_scenes:
                scenes_a_resumir = scenes[:-scenes_puros]
                scenes_puros = scenes[-scenes_puros:]
                bodies_a_resumir = [scene.resumen for scene in scenes_a_resumir]
                bodies_puros = [scene.resumen for scene in scenes_puros]
                SceneManager.mark_scenes_as_summarized(self.db, scenes_a_resumir)  # Marca las escenas como resumidas
                return campaign_resumen, story_resumen, bodies_a_resumir, bodies_puros
            else:
                scene_bodies = [scene.resumen for scene in scenes]
                return campaign_resumen, story_resumen, [], scene_bodies  
                

    def obtener_contexto_ambientacion_y_reglas(self, campaign_id):
        """
        Recupera y devuelve el json del contexto de ambientación y reglas para la campaña dada.
        """
        ruleset = RulesetManager.get_ruleset_by_campaign_id(self.db, campaign_id)
        ruleset = self.db.query(Ruleset).filter(Ruleset.campaign_id == campaign_id, Ruleset.activo == True).first()
        if ruleset and ruleset.ambientacion_json and ruleset.reglas_json:
            return ruleset.ambientacion_json, ruleset.reglas_json
        return None, None

    def obtener_hojas_personaje_y_estado_actual(self, character_ids):
        """
        Recupera y devuelve el json de las hojas de personaje y su estado actual para los personajes dados.
        """
        hojas_personaje = []
        estado_actual_personaje = []

        for character_id in character_ids:
            character = CharacterManager.get_character_by_id(self.db, character_id)
            if character:
                hojas_personaje.append(character.hoja_json)
                estado_actual_personaje.append(character.estado_json)

        return {
            "hojas_personaje": hojas_personaje,
            "estado_actual_personaje": estado_actual_personaje
        }
        

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
        if 'scene' in contexto and 'story' in contexto:
            campaign_id = contexto['story'].get('campaign_id')
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
