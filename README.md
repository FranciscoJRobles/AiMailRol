# AiMailRol

Sistema de combate por email usando Gmail, desarrollado en Python.

## Descripción
Este proyecto permite gestionar "combates" por email entre varios jugadores, utilizando la API de Gmail. El sistema detecta respuestas de los jugadores, mantiene el hilo de conversación y solo responde automáticamente cuando todos los jugadores han contestado en la ronda actual. Soporta múltiples rondas/ciclos y es persistente mediante archivos JSON.

## Características
- Consulta automática de emails no leídos cada 15 segundos.
- Procesamiento de emails con palabras clave específicas ([COMBATE], [TEST]).
- Responde solo cuando todos los jugadores han respondido en la ronda actual.
- Soporte para múltiples rondas/ciclos de respuestas.
- Persistencia de estado en archivos JSON (`combates.json`, `jugadores.json`).
- Gestión de jugadores desde archivo JSON.
- Mantiene el hilo de conversación en Gmail.
- Modular y escalable.
- Protección ante archivos vacíos/corruptos.
- Limpieza automática de combates inactivos.

## Estructura del proyecto
- `main.py`: Punto de entrada. Permite iniciar el combate con argumento.
- `services/`
  - `gmail_service.py`: Acceso a Gmail (OAuth2, fetch, send, marcar leído).
  - `combate_manager.py`: Lógica y persistencia de combates por rondas.
  - `jugadores_manager.py`: Gestión de jugadores.
- `models/`
  - `email.py`: Modelo de email.
- `jobs/`
  - `email_cron.py`: Tarea periódica de consulta y procesamiento de emails.
- `jsondata/`
  - `combates.json`: Estado de los combates.
  - `jugadores.json`: Lista de jugadores.
- `config/`
  - `credentials.json`, `token.json`: Credenciales OAuth2 de Gmail.

## Instalación
1. Clona el repositorio.
2. Crea un entorno virtual e instala las dependencias necesarias (`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, etc.).
3. Coloca tus credenciales de Gmail en `config/credentials.json`.
4. Configura la lista de jugadores en `jsondata/jugadores.json`.

## Uso
- Ejecuta `main.py` para iniciar el sistema.
- Usa el argumento correspondiente para enviar el mensaje inicial de combate.
- El sistema gestionará automáticamente las rondas y respuestas.

## Notas
- No subas archivos sensibles ni credenciales al repositorio (ver `.gitignore`).
- El sistema es extensible para nuevas reglas de combate o integración con otras plataformas.

## Estado actual
- Refactorización completada para soportar rondas/ciclos indefinidos.
- Persistencia robusta y modularidad asegurada.
- Listo para pruebas y mejoras de trazabilidad/logs.

---

¿Dudas o sugerencias? ¡Abre un issue o contacta al autor!
