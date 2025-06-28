"""
Nodo para validación de reglas del juego.
Valida acciones contra el ruleset de la campaña.
"""

from typing import Dict, Any, List
from ..states.email_state import EmailState
from ia.ia_client import IAClient
import logging
import json

logger = logging.getLogger(__name__)

class RulesValidationNode:
    """Nodo encargado de validar acciones contra las reglas del juego."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="precisa")
    
    def __call__(self, state: EmailState) -> EmailState:
        """
        Valida las intenciones del email contra las reglas de la campaña.
        
        Args:
            state: Estado con intenciones analizadas y ruleset
            
        Returns:
            Estado actualizado con validaciones aplicadas
        """
        try:
            logger.info("Iniciando validación de reglas")
            
            # Si no hay intenciones o ruleset, saltear validación
            if not state.get('intenciones') or not state.get('ruleset'):
                logger.info("No hay intenciones o ruleset, saltando validación")
                state['validaciones'] = []
                return state
            
            validaciones = []
            
            # Filtrar intenciones que requieren validación
            intenciones_a_validar = [
                intencion for intencion in state['intenciones']
                if intencion.get('tipo') in [
                    'accion_con_tirada', 
                    'combate', 
                    'accion_sencilla'
                ]
            ]
            
            if not intenciones_a_validar:
                logger.info("No hay intenciones que requieran validación")
                state['validaciones'] = []
                return state
            
            # Construir prompt para validación
            reglas_texto = state['ruleset'].get('reglas', '')
            personaje_info = self._get_character_info(state)
            
            for intencion in intenciones_a_validar:
                validacion = self._validate_intention(
                    intencion, 
                    reglas_texto, 
                    personaje_info,
                    state.get('estado_actual', 'narracion')
                )
                validaciones.append(validacion)
            
            state['validaciones'] = validaciones
            logger.info(f"Validación completada. {len(validaciones)} acciones validadas")
            
        except Exception as e:
            logger.error(f"Error en validación de reglas: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en validación: {str(e)}")
            state['validaciones'] = []
        
        return state
    
    def _get_character_info(self, state: EmailState) -> Dict[str, Any]:
        """Obtiene información del personaje que está actuando."""
        if not state.get('character_id') or not state.get('personajes_pj'):
            return {}
        
        for personaje in state['personajes_pj']:
            if personaje.get('id') == state['character_id']:
                return personaje
        
        return {}
    
    def _validate_intention(
        self, 
        intencion: Dict[str, Any], 
        reglas: str, 
        personaje: Dict[str, Any],
        estado_juego: str
    ) -> Dict[str, Any]:
        """
        Valida una intención específica contra las reglas.
        
        Args:
            intencion: Intención a validar
            reglas: Texto de las reglas del juego
            personaje: Información del personaje
            estado_juego: Estado actual del juego
            
        Returns:
            Diccionario con el resultado de la validación
        """
        try:
            prompt = f"""
            Eres un validador de reglas para un juego de rol narrativo. 
            
            REGLAS DEL JUEGO:
            {reglas}
            
            PERSONAJE:
            {json.dumps(personaje, indent=2, ensure_ascii=False)}
            
            ESTADO DEL JUEGO: {estado_juego}
            
            ACCIÓN A VALIDAR:
            Tipo: {intencion.get('tipo')}
            Descripción: {intencion.get('bloque')}
            Entidades: {json.dumps(intencion.get('entidades', {}), ensure_ascii=False)}
            
            Valida si esta acción es posible según las reglas y el estado del personaje.
            
            Responde en JSON con esta estructura:
            {{
                "valida": true/false,
                "razon": "explicación de por qué es válida o inválida",
                "requiere_tirada": true/false,
                "dificultad": "fácil/normal/difícil/muy_difícil" (solo si requiere tirada),
                "modificadores": ["lista de modificadores aplicables"],
                "consecuencias": "posibles consecuencias de la acción"
            }}
            """
            
            contexto = {"sistema": prompt, "historial": []}
            respuesta = self.ia_client.procesar_mensaje(
                "Valida esta acción", 
                contexto, 
                "precisa"
            )
            
            try:
                validacion_data = json.loads(respuesta)
                validacion_data['intencion_original'] = intencion
                return validacion_data
            except json.JSONDecodeError:
                return {
                    "intencion_original": intencion,
                    "valida": True,  # Por defecto permitir si no se puede parsear
                    "razon": "No se pudo validar automáticamente",
                    "requiere_tirada": False,
                    "modificadores": [],
                    "consecuencias": "Desconocidas"
                }
                
        except Exception as e:
            logger.error(f"Error validando intención: {e}")
            return {
                "intencion_original": intencion,
                "valida": True,  # Por defecto permitir en caso de error
                "razon": f"Error en validación: {str(e)}",
                "requiere_tirada": False,
                "modificadores": [],
                "consecuencias": "Error en validación"
            }

# Función helper para usar en el grafo
def validate_rules_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = RulesValidationNode()
    return node(state)
