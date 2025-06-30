import os
import logging

class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

def configure_logging():
    """Configura el sistema de logging con diferentes niveles y archivos."""
    # Crear la carpeta 'logs' si no existe
    os.makedirs('logs', exist_ok=True)

    # Crear un logger
    logger = logging.getLogger("multi_level_logger")
    logger.setLevel(logging.DEBUG)  # Nivel mínimo para el logger
    logger.propagate = False  # Evitar propagación

    # Formato común para los logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Manejador para mensajes DEBUG
    debug_handler = logging.FileHandler('logs/debug.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    debug_handler.addFilter(LevelFilter(logging.DEBUG))

    # Manejador para mensajes INFO
    info_handler = logging.FileHandler('logs/info.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(LevelFilter(logging.INFO))

    # Manejador para mensajes ERROR
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    # Agregar los manejadores al logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger
