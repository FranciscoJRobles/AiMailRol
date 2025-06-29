"""
Ejemplos de uso del OrquestadorLangGraph.
"""

from ia.langgraph import orquestador_langgraph
from api.core.database import SessionLocal
import logging

# Configurar logging para ver qué está pasando
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ejemplo_procesar_siguiente_email():
    """Ejemplo: Procesar el siguiente email pendiente."""
    print("\n=== EJEMPLO: Procesar Siguiente Email Pendiente ===")
    
    # Procesar siguiente email pendiente (email_id=None)
    resultado = orquestador_langgraph.procesar_email()
    
    if resultado['success']:
        if resultado.get('reason') == 'no_pending_emails':
            print("ℹ️  No hay emails pendientes para procesar")
        else:
            email_id = resultado.get('email_id', 'unknown')
            print(f"✅ Email {email_id} procesado exitosamente")
            print(f"   Respuesta generada: {resultado.get('respuesta_generada', 'N/A')[:100]}...")
    else:
        print(f"❌ Error procesando email: {resultado.get('error')}")
    
    return resultado

def ejemplo_procesar_lote():
    """Ejemplo: Procesar múltiples emails en lote."""
    print("\n=== EJEMPLO: Procesamiento en Lote ===")
    
    # Procesar hasta 5 emails pendientes
    resultado = orquestador_langgraph.procesar_emails_pendientes(max_emails=5)
    
    if resultado['success']:
        emails_procesados = resultado.get('emails_procesados', 0)
        emails_exitosos = resultado.get('emails_exitosos', 0)
        emails_error = resultado.get('emails_con_error', 0)
        
        if emails_procesados == 0:
            print("ℹ️  No había emails pendientes para procesar")
        else:
            print(f"📊 Resumen del procesamiento:")
            print(f"   • Total procesados: {emails_procesados}")
            print(f"   • Exitosos: {emails_exitosos}")
            print(f"   • Con errores: {emails_error}")
            
            # Mostrar errores si los hay
            if resultado.get('errores'):
                print("   • Errores detallados:")
                for error in resultado['errores'][:3]:  # Solo primeros 3
                    print(f"     - Email {error['email_id']}: {error['error']}")
    else:
        print(f"❌ Error en procesamiento en lote: {resultado.get('error')}")
    
    return resultado

if __name__ == "__main__":
    print("🚀 EJEMPLOS DE USO - OrquestadorLangGraph")
    print("=" * 50)
    
    # Ejecutar ejemplos
    try:
        ejemplo_procesar_siguiente_email()
        ejemplo_procesar_lote()
        
    except Exception as e:
        print(f"❌ Error ejecutando ejemplos: {e}")
        logger.exception("Error detallado:")
    
    print("\n✅ Ejemplos completados")
