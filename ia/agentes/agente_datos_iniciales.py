# ia/agentes/agente_contexto_inicial.py
"""
Agente encargado de cargar y ensamblar todo el contexto inicial relevante para el flujo de IA de la partida de rol.
"""


from api.managers.story_state_manager import StoryStateManager
from api.managers.campaign_manager import CampaignManager
from api.managers.ruleset_manager import RulesetManager
from api.managers.character_manager import CharacterManager
from api.managers.scene_manager import SceneManager
from ia.agentes.subagentes.subagente_gestor_emails import SubagenteGestorEmails
from api.schemas.scene import SceneOut
from api.schemas.story_state import StoryStateOut
from api.schemas.campaign import CampaignOut
from api.schemas.ruleset import RulesetOut
from api.schemas.character import CharacterOut

class AgenteDatosIniciales:
    def __init__(self, db, resumidor_textos=None, email=None):
        self.db = db
        self.resumidor_textos = resumidor_textos

    def cargar_datos_iniciales(self, scene_id, max_emails=10, n_puros=3):
        """
        Carga y ensambla todo el contexto relevante para la escena indicada.
        Devuelve un diccionario con toda la información necesaria para el flujo IA.
        """
        contexto = {}

        # 1. Escena
        scene = SceneManager.get_scene_by_id(self.db, scene_id)
        contexto['scene'] = SceneOut.model_validate(scene).model_dump() if scene else None

        # 2. StoryState
        story_state = StoryStateManager().get_story_state_by_id(self.db, scene.story_state_id) if scene and scene.story_state_id else None
        contexto['story_state'] = StoryStateOut.model_validate(story_state).model_dump() if story_state else None

        # 3. Campaign
        campaign = CampaignManager().get_campaign_story_states(self.db, story_state['campaign_id']) if story_state and story_state.get('campaign_id') else None
        contexto['campaign'] = CampaignOut.model_validate(campaign).model_dump() if campaign else None

        # 4. Ruleset
        ruleset = RulesetManager().get_ruleset_by_campaign_id(self.db, campaign.id) 
        contexto['ruleset'] = RulesetOut.model_validate(ruleset).model_dump() if ruleset else None

        # 5. Personajes y sus estados
        personajes = StoryStateManager().get_characters_by_story_state_id(self.db, story_state.id) if scene else []
        contexto['personajes'] = [CharacterOut.model_validate(p).model_dump() for p in personajes]

        # 6. Emails relevantes
        gestor_emails = SubagenteGestorEmails(self.db)
        emails_contexto = gestor_emails.gestionar_emails_para_contexto(scene_id, max_emails, n_puros)
        contexto['emails_contexto'] = emails_contexto

        # 7. (Opcional) Resúmenes IA
        # Puedes añadir aquí lógica para resumir emails, historia, etc. usando self.resumidor_textos

        return contexto
