"""
Ejemplo de uso del nuevo sistema LangGraph para procesamiento de emails.
"""

from ia.langgraph import orquestador_langgraph, EmailProcessingGraph, CombatResolutionGraph
from api.core.database import SessionLocal
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ejemplo_procesamiento_individual():
    """Ejemplo de procesamiento de un email individual."""
    print("=== Ejemplo: Procesamiento Individual ===")
    
    # Procesar un email específico (reemplaza 123 con un ID real)
    email_id = 123
    resultado = orquestador_langgraph.procesar_email(email_id)
    
    print(f"Resultado: {resultado}")
    
    if resultado.get('success'):
        print("✅ Email procesado exitosamente")
        if resultado.get('respuesta_generada'):
            print(f"Respuesta generada: {resultado['respuesta_generada'][:100]}...")
    else:
        print("❌ Error procesando email")
        print(f"Error: {resultado.get('error')}")

def ejemplo_procesamiento_lote():
    """Ejemplo de procesamiento en lote."""
    print("\n=== Ejemplo: Procesamiento en Lote ===")
    
    # Procesar hasta 5 emails pendientes
    resultado = orquestador_langgraph.procesar_emails_pendientes(max_emails=5)
    
    print(f"Emails procesados: {resultado.get('emails_procesados', 0)}")
    print(f"Emails exitosos: {resultado.get('emails_exitosos', 0)}")
    print(f"Emails con error: {resultado.get('emails_con_error', 0)}")
    
    if resultado.get('errores'):
        print("\nErrores encontrados:")
        for error in resultado['errores']:
            print(f"  - Email {error['email_id']}: {error['error']}")

def ejemplo_uso_grafo_directo():
    """Ejemplo de uso directo de un grafo específico."""
    print("\n=== Ejemplo: Uso Directo de Grafo ===")
    
    db_session = SessionLocal()
    
    try:
        # Usar el grafo de email normal
        email_graph = EmailProcessingGraph()
        resultado = email_graph.process_email(
            email_id=123,  # Reemplaza con ID real
            db_session=db_session,
            current_state="narracion"
        )
        
        print(f"Resultado del grafo: {resultado}")
        
        # Usar el grafo de combate
        combat_graph = CombatResolutionGraph()
        resultado_combate = combat_graph.process_combat_email(
            email_id=124,  # Reemplaza con ID real
            db_session=db_session,
            current_state="accion_en_turno"
        )
        
        print(f"Resultado del combate: {resultado_combate}")
        
    finally:
        db_session.close()

def ejemplo_streaming():
    """Ejemplo de monitoreo en tiempo real del procesamiento."""
    print("\n=== Ejemplo: Streaming de Eventos ===")
    
    db_session = SessionLocal()
    
    try:
        email_graph = EmailProcessingGraph()
        
        # Stream de eventos para monitoreo
        for evento in email_graph.process_email_stream(
            email_id=123,  # Reemplaza con ID real
            db_session=db_session
        ):
            print(f"Evento: {evento}")
            
    finally:
        db_session.close()

def ejemplo_estadisticas():
    """Ejemplo de obtención de estadísticas."""
    print("\n=== Ejemplo: Estadísticas del Sistema ===")
    
    stats = orquestador_langgraph.get_processing_stats()
    
    print(f"Emails pendientes: {stats.get('emails_pendientes', 0)}")
    print(f"Emails procesados hoy: {stats.get('emails_procesados_hoy', 0)}")
    print(f"Estados de juego activos: {stats.get('estados_juego_activos', 0)}")
    print(f"Grafos disponibles: {stats.get('grafos_disponibles', [])}")

def ejemplo_visualizacion_grafo():
    """Ejemplo de visualización del flujo del grafo."""
    print("\n=== Ejemplo: Visualización del Grafo ===")
    
    email_graph = EmailProcessingGraph()
    visualizacion = email_graph.get_graph_visualization()
    
    print("Flujo del grafo de emails:")
    print(visualizacion)

if __name__ == "__main__":
    # Ejecutar todos los ejemplos
    try:
        ejemplo_procesamiento_individual()
        ejemplo_procesamiento_lote()
        ejemplo_uso_grafo_directo()
        ejemplo_streaming()
        ejemplo_estadisticas()
        ejemplo_visualizacion_grafo()
        
    except Exception as e:
        logger.error(f"Error en ejemplo: {e}")
        print(f"❌ Error ejecutando ejemplos: {e}")
    
    print("\n🎉 Ejemplos completados")
