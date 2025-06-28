"""
Cadenas especializadas para generación de respuestas elaboradas.
"""

from typing import Dict, Any, List
from ia.ia_client import IAClient
import logging
import json

logger = logging.getLogger(__name__)

class ResponseChain:
    """Cadena para generación de respuestas en múltiples pasos."""
    
    def __init__(self):
        self.ia_client_creativa = IAClient(perfil="creativa")
        self.ia_client_precisa = IAClient(perfil="precisa")
    
    def generate_elaborated_response(
        self, 
        context: Dict[str, Any],
        intenciones: List[Dict[str, Any]],
        validaciones: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta elaborada en múltiples pasos.
        
        Args:
            context: Contexto completo del juego
            intenciones: Intenciones analizadas del email
            validaciones: Validaciones aplicadas
            
        Returns:
            Respuesta elaborada con metadatos
        """
        try:
            # Paso 1: Planificación de la respuesta
            plan = self._plan_response(context, intenciones, validaciones)
            
            # Paso 2: Generación del borrador
            borrador = self._generate_draft(plan, context)
            
            # Paso 3: Revisión y refinamiento
            respuesta_final = self._refine_response(borrador, plan, context)
            
            # Paso 4: Validación final
            validacion_final = self._validate_final_response(respuesta_final, context)
            
            return {
                'plan': plan,
                'borrador': borrador,
                'respuesta_final': respuesta_final,
                'validacion': validacion_final,
                'calidad': validacion_final.get('puntuacion', 7)
            }
            
        except Exception as e:
            logger.error(f"Error en generación elaborada: {e}")
            return {
                'error': str(e),
                'respuesta_final': "Lo siento, ha ocurrido un error generando la respuesta.",
                'calidad': 1
            }
    
    def _plan_response(
        self, 
        context: Dict[str, Any], 
        intenciones: List[Dict[str, Any]],
        validaciones: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Planifica la estructura de la respuesta."""
        prompt = f"""
        Eres un planificador narrativo para un juego de rol. Crea un plan estructurado 
        para responder a las acciones del jugador.
        
        CONTEXTO DEL JUEGO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        INTENCIONES DEL JUGADOR:
        {json.dumps(intenciones, indent=2, ensure_ascii=False)}
        
        VALIDACIONES APLICADAS:
        {json.dumps(validaciones or [], indent=2, ensure_ascii=False)}
        
        Crea un plan que incluya:
        1. Estructura de la respuesta (introducción, desarrollo, conclusión)
        2. Elementos narrativos a incluir
        3. Tono y estilo apropiado
        4. Información que debe ser comunicada
        5. Posibles consecuencias a mencionar
        
        Responde en JSON con esta estructura.
        """
        
        try:
            contexto_ia = {"sistema": prompt, "historial": []}
            respuesta = self.ia_client_precisa.procesar_mensaje(
                "Crea el plan de respuesta", 
                contexto_ia, 
                "precisa"
            )
            
            return json.loads(respuesta)
            
        except Exception as e:
            logger.error(f"Error en planificación: {e}")
            return {
                'estructura': ['introducción', 'desarrollo', 'conclusión'],
                'tono': 'narrativo',
                'elementos_clave': [],
                'error': str(e)
            }
    
    def _generate_draft(self, plan: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Genera el borrador inicial de la respuesta."""
        prompt = f"""
        Basándote en este plan, genera un borrador de respuesta narrativa:
        
        PLAN:
        {json.dumps(plan, indent=2, ensure_ascii=False)}
        
        CONTEXTO:
        Sistema: {context.get('contexto_sistema', '')}
        Historial: {context.get('contexto_historial', [])}
        
        Genera una respuesta narrativa inmersiva que siga el plan establecido.
        Escribe como un narrador de rol dirigiéndote al jugador en segunda persona.
        """
        
        try:
            contexto_ia = {
                "sistema": prompt,
                "historial": context.get('contexto_historial', [])
            }
            
            borrador = self.ia_client_creativa.procesar_mensaje(
                "Genera el borrador narrativo",
                contexto_ia,
                "creativa"
            )
            
            return borrador
            
        except Exception as e:
            logger.error(f"Error generando borrador: {e}")
            return "Ha ocurrido un error generando la respuesta inicial."
    
    def _refine_response(
        self, 
        borrador: str, 
        plan: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Refina y mejora el borrador."""
        prompt = f"""
        Revisa y mejora este borrador de respuesta narrativa:
        
        BORRADOR:
        {borrador}
        
        PLAN ORIGINAL:
        {json.dumps(plan, indent=2, ensure_ascii=False)}
        
        Mejora el borrador asegurándote de que:
        1. Sigue el plan establecido
        2. Mantiene inmersión narrativa
        3. Es coherente con el contexto
        4. Tiene buen ritmo y fluidez
        5. Incluye todos los elementos necesarios
        
        Devuelve SOLO la versión mejorada del texto.
        """
        
        try:
            contexto_ia = {"sistema": prompt, "historial": []}
            respuesta_refinada = self.ia_client_creativa.procesar_mensaje(
                borrador,
                contexto_ia,
                "creativa"
            )
            
            return respuesta_refinada
            
        except Exception as e:
            logger.error(f"Error refinando respuesta: {e}")
            return borrador  # Retornar borrador original si falla el refinamiento
    
    def _validate_final_response(
        self, 
        respuesta: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida la calidad de la respuesta final."""
        prompt = f"""
        Evalúa la calidad de esta respuesta narrativa de juego de rol:
        
        RESPUESTA:
        {respuesta}
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Evalúa estos aspectos (puntuación 1-10):
        1. Inmersión narrativa
        2. Coherencia con el contexto
        3. Calidad de escritura
        4. Relevancia para el jugador
        5. Avance de la historia
        
        Responde en JSON con:
        {{
            "puntuacion_inmersion": 0-10,
            "puntuacion_coherencia": 0-10,
            "puntuacion_escritura": 0-10,
            "puntuacion_relevancia": 0-10,
            "puntuacion_avance": 0-10,
            "puntuacion": 0-10 (promedio),
            "comentarios": "comentarios sobre la calidad",
            "mejoras_sugeridas": ["lista de mejoras posibles"]
        }}
        """
        
        try:
            contexto_ia = {"sistema": prompt, "historial": []}
            evaluacion = self.ia_client_precisa.procesar_mensaje(
                respuesta,
                contexto_ia,
                "precisa"
            )
            
            return json.loads(evaluacion)
            
        except Exception as e:
            logger.error(f"Error validando respuesta: {e}")
            return {
                'puntuacion': 7,  # Puntuación por defecto
                'comentarios': f'Error en validación: {str(e)}',
                'mejoras_sugeridas': []
            }

class AdaptiveResponseChain:
    """Cadena que adapta el estilo de respuesta según el contexto."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="creativa")
    
    def generate_adaptive_response(
        self, 
        context: Dict[str, Any],
        player_style: str = "standard",
        scene_type: str = "general"
    ) -> str:
        """
        Genera una respuesta adaptada al estilo del jugador y tipo de escena.
        
        Args:
            context: Contexto del juego
            player_style: Estilo preferido del jugador
            scene_type: Tipo de escena (combate, social, exploración, etc.)
            
        Returns:
            Respuesta adaptada
        """
        try:
            # Configurar estilo basado en preferencias
            style_configs = {
                "conciso": {
                    "longitud": "breve",
                    "detalle": "bajo",
                    "estilo": "directo"
                },
                "detallado": {
                    "longitud": "extensa",
                    "detalle": "alto",
                    "estilo": "descriptivo"
                },
                "cinematico": {
                    "longitud": "media",
                    "detalle": "alto",
                    "estilo": "visual"
                },
                "standard": {
                    "longitud": "media",
                    "detalle": "medio",
                    "estilo": "narrativo"
                }
            }
            
            style_config = style_configs.get(player_style, style_configs["standard"])
            
            # Configurar según tipo de escena
            scene_configs = {
                "combate": {
                    "ritmo": "rápido",
                    "tension": "alta",
                    "foco": "acción"
                },
                "social": {
                    "ritmo": "pausado",
                    "tension": "variable",
                    "foco": "diálogo"
                },
                "exploración": {
                    "ritmo": "medio",
                    "tension": "media",
                    "foco": "descripción"
                },
                "general": {
                    "ritmo": "medio",
                    "tension": "media",
                    "foco": "narrativa"
                }
            }
            
            scene_config = scene_configs.get(scene_type, scene_configs["general"])
            
            # Generar respuesta adaptada
            prompt = f"""
            Genera una respuesta narrativa adaptada a estas especificaciones:
            
            ESTILO DEL JUGADOR:
            - Longitud: {style_config['longitud']}
            - Nivel de detalle: {style_config['detalle']}
            - Estilo narrativo: {style_config['estilo']}
            
            TIPO DE ESCENA:
            - Ritmo: {scene_config['ritmo']}
            - Tensión: {scene_config['tension']}
            - Foco principal: {scene_config['foco']}
            
            CONTEXTO:
            {json.dumps(context, indent=2, ensure_ascii=False)}
            
            Adapta tu respuesta a estas especificaciones manteniendo la calidad narrativa.
            """
            
            contexto_ia = {
                "sistema": prompt,
                "historial": context.get('contexto_historial', [])
            }
            
            respuesta = self.ia_client.procesar_mensaje(
                "Genera respuesta adaptada",
                contexto_ia,
                "creativa"
            )
            
            return respuesta
            
        except Exception as e:
            logger.error(f"Error en respuesta adaptiva: {e}")
            return "Ha ocurrido un error generando la respuesta adaptada."
