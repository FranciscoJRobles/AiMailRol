import time
import threading
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.managers.email_manager import EmailManager
from ia.langgraph.orquestador_langgraph import orquestador_langgraph

def start_email_db_processor(intervalo_segundos=5):
    """
    Cron que verifica cada X segundos si debe procesar emails.
    Solo se ejecuta si no hay otro proceso de emails en marcha.
    """
    is_processing = False
    processing_lock = threading.Lock()
    print(f"Iniciando cron de emails de base de datos (cada {intervalo_segundos} segundos)...")
    
    while True:
        try:
            # Verificar si ya se está procesando
            with processing_lock:
                if is_processing:
                    print("Proceso de emails de base de datos ya en ejecución. Esperando...")
                    time.sleep(intervalo_segundos)
                    continue
                
                # Marcar como en proceso
                is_processing = True
            
            print("Iniciando procesamiento de emails pendientes...")
            # Usar el nuevo orquestador LangGraph
            resultado = orquestador_langgraph.procesar_emails_pendientes(max_emails=5)
            
            if resultado.get('success'):
                emails_procesados = resultado.get('emails_procesados', 0)
                emails_exitosos = resultado.get('emails_exitosos', 0)
                
                if emails_procesados == 0:
                    print("No había emails pendientes para procesar")
                else:
                    print(f"Procesamiento completado: {emails_exitosos}/{emails_procesados} emails exitosos")
                
                if resultado.get('errores'):
                    print(f"Errores encontrados: {len(resultado['errores'])}")
                    for error in resultado['errores'][:3]:  # Mostrar solo los primeros 3 errores
                        print(f"  - Email {error['email_id']}: {error['error']}")
            else:
                print(f"Error en procesamiento: {resultado.get('error', 'Error desconocido')}") 
            
        except Exception as e:
            print(f"Error en cron de emails: {e}")
            
        finally:
            # Liberar el lock
            with processing_lock:
                is_processing = False
            print("Procesamiento de emails de base de datos completado. Esperando al próximo ciclo...")
            
        time.sleep(intervalo_segundos)