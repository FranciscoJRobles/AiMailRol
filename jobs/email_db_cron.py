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
            resultado = orquestador_langgraph.procesar_email()
            
            if resultado.get('success') == True:
                # Aquí podrías guardar el resultado en la base de datos si es necesario                
                print(f"Email procesado exitosamente: {resultado.get('email_id')}")
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