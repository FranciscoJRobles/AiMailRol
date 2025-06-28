"""
Cadenas especializadas para análisis complejos de emails.
"""

from typing import List, Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ia.ia_client import IAClient
import logging

logger = logging.getLogger(__name__)

class AnalysisChain:
    """Cadena para análisis complejos de emails largos o ambiguos."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="clasificacion")
    
    def analyze_complex_email(
        self, 
        email_text: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Análisis en múltiples pasos para emails complejos.
        
        Args:
            email_text: Texto del email a analizar
            context: Contexto adicional (personajes, estado del juego, etc.)
            
        Returns:
            Análisis detallado del email
        """
        try:
            # Paso 1: Segmentación inicial
            segmentos = self._segment_email(email_text)
            
            # Paso 2: Análisis de cada segmento
            analisis_segmentos = []
            for segmento in segmentos:
                analisis = self._analyze_segment(segmento, context)
                analisis_segmentos.append(analisis)
            
            # Paso 3: Síntesis final
            sintesis = self._synthesize_analysis(analisis_segmentos, context)
            
            return {
                'segmentos': segmentos,
                'analisis_individual': analisis_segmentos,
                'sintesis': sintesis,
                'complejidad': 'alta' if len(segmentos) > 3 else 'media'
            }
            
        except Exception as e:
            logger.error(f"Error en análisis complejo: {e}")
            return {
                'error': str(e),
                'segmentos': [email_text],
                'analisis_individual': [],
                'sintesis': {},
                'complejidad': 'error'
            }
    
    def _segment_email(self, email_text: str) -> List[str]:
        """Segmenta el email en partes lógicas."""
        prompt = """
        Divide este email en segmentos lógicos separados. Cada segmento debe contener
        una idea, acción o diálogo completo.
        
        EMAIL:
        {email_text}
        
        Devuelve una lista de segmentos separados por "---SEGMENT---"
        """
        
        try:
            contexto = {"sistema": prompt, "historial": []}
            respuesta = self.ia_client.procesar_mensaje(
                email_text, 
                contexto, 
                "clasificacion"
            )
            
            # Separar por el delimitador
            segmentos = [s.strip() for s in respuesta.split("---SEGMENT---") if s.strip()]
            
            # Si no hay segmentación clara, usar párrafos
            if len(segmentos) <= 1:
                segmentos = [p.strip() for p in email_text.split('\n\n') if p.strip()]
            
            return segmentos if segmentos else [email_text]
            
        except Exception:
            # Fallback: dividir por párrafos
            return [p.strip() for p in email_text.split('\n\n') if p.strip()]
    
    def _analyze_segment(self, segmento: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analiza un segmento individual."""
        personajes_info = ""
        if context and context.get('personajes_pj'):
            nombres = [p.get('nombre', '') for p in context['personajes_pj']]
            personajes_info = f"Personajes jugadores: {', '.join(nombres)}"
        
        prompt = f"""
        Analiza este segmento de email de juego de rol:
        
        {personajes_info}
        
        SEGMENTO: {segmento}
        
        Identifica:
        1. Tipo de contenido (acción, diálogo, pensamiento, meta, etc.)
        2. Personajes mencionados
        3. Intención principal
        4. Urgencia/importancia (1-5)
        5. Requiere respuesta inmediata (sí/no)
        
        Responde en JSON.
        """
        
        try:
            contexto = {"sistema": prompt, "historial": []}
            respuesta = self.ia_client.procesar_mensaje(
                segmento, 
                contexto, 
                "clasificacion"
            )
            
            import json
            return json.loads(respuesta)
            
        except Exception as e:
            return {
                'segmento': segmento,
                'tipo': 'desconocido',
                'error': str(e),
                'urgencia': 3,
                'requiere_respuesta': True
            }
    
    def _synthesize_analysis(
        self, 
        analisis_segmentos: List[Dict[str, Any]], 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Sintetiza el análisis de todos los segmentos."""
        try:
            # Extraer información clave
            tipos_contenido = [a.get('tipo', 'desconocido') for a in analisis_segmentos]
            urgencias = [a.get('urgencia', 3) for a in analisis_segmentos if isinstance(a.get('urgencia'), int)]
            
            # Calcular métricas
            urgencia_promedio = sum(urgencias) / len(urgencias) if urgencias else 3
            requiere_respuesta_inmediata = any(a.get('requiere_respuesta', False) for a in analisis_segmentos)
            
            # Determinar acción recomendada
            if urgencia_promedio >= 4 or requiere_respuesta_inmediata:
                accion_recomendada = "respuesta_inmediata"
            elif urgencia_promedio >= 3:
                accion_recomendada = "respuesta_normal"
            else:
                accion_recomendada = "respuesta_diferida"
            
            return {
                'tipos_contenido': tipos_contenido,
                'urgencia_promedio': urgencia_promedio,
                'requiere_respuesta_inmediata': requiere_respuesta_inmediata,
                'accion_recomendada': accion_recomendada,
                'num_segmentos': len(analisis_segmentos)
            }
            
        except Exception as e:
            logger.error(f"Error en síntesis: {e}")
            return {
                'error': str(e),
                'accion_recomendada': "respuesta_normal"
            }

class HierarchicalAnalysisChain:
    """Cadena para análisis jerárquico de emails con múltiples niveles."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="clasificacion")
    
    def analyze_hierarchical(
        self, 
        email_text: str, 
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        Análisis jerárquico en múltiples niveles de profundidad.
        
        Args:
            email_text: Texto a analizar
            depth: Profundidad del análisis (1-5)
            
        Returns:
            Análisis jerárquico estructurado
        """
        try:
            resultado = {
                'texto_original': email_text,
                'niveles': {}
            }
            
            texto_actual = email_text
            
            for nivel in range(1, depth + 1):
                analisis_nivel = self._analyze_level(texto_actual, nivel)
                resultado['niveles'][f'nivel_{nivel}'] = analisis_nivel
                
                # Preparar texto para siguiente nivel (más específico)
                if analisis_nivel.get('elementos_clave'):
                    texto_actual = '\n'.join(analisis_nivel['elementos_clave'])
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en análisis jerárquico: {e}")
            return {'error': str(e), 'niveles': {}}
    
    def _analyze_level(self, texto: str, nivel: int) -> Dict[str, Any]:
        """Analiza un nivel específico de profundidad."""
        prompts_por_nivel = {
            1: "Identifica los temas principales y estructura general del texto.",
            2: "Analiza las intenciones específicas y acciones detalladas.",
            3: "Examina subtextos, emociones y motivaciones implícitas."
        }
        
        prompt_base = prompts_por_nivel.get(nivel, "Analiza en detalle este texto.")
        
        prompt = f"""
        {prompt_base}
        
        TEXTO: {texto}
        
        Nivel de análisis: {nivel}
        
        Devuelve JSON con:
        - elementos_clave: lista de elementos importantes encontrados
        - patrones: patrones identificados en este nivel
        - insights: conocimientos específicos de este nivel
        """
        
        try:
            contexto = {"sistema": prompt, "historial": []}
            respuesta = self.ia_client.procesar_mensaje(
                texto, 
                contexto, 
                "clasificacion"
            )
            
            import json
            return json.loads(respuesta)
            
        except Exception as e:
            return {
                'nivel': nivel,
                'error': str(e),
                'elementos_clave': [],
                'patrones': [],
                'insights': []
            }
