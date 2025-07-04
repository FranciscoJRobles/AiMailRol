# AiMailRol Backend

Backend para un sistema de rol multijugador por email, con integración de IA y arquitectura moderna basada en FastAPI y SQLAlchemy. Permite la gestión flexible de campañas, subtramas, escenas, personajes y turnos, soportando relaciones complejas y actualizaciones parciales.

## Características principales
- **FastAPI** para endpoints RESTful modernos y documentación automática.
- **SQLAlchemy** para ORM y gestión de relaciones 1:N y M:N entre entidades.
- **Pydantic** para validación de datos y schemas de entrada/salida.
- **Integración con IA** para automatización y generación de contenido.
- **Procesamiento inteligente de emails de rol**: segmentación y clasificación de intenciones usando IA.
- **Gestión de campañas, personajes, escenas, turnos, reglas y estados de historia**.
- **Actualizaciones parciales (PATCH/PUT)** y endpoints para asociar/desasociar entidades.
- **Separación clara de modelos, schemas, managers y endpoints**.

## Novedades recientes

- **Eliminación de la capa CRUD**:  
  Toda la lógica de negocio y acceso a datos se ha consolidado en los Managers, simplificando la arquitectura y reduciendo redundancias.
- **Clasificación de intenciones centralizada**:  
  La lista de intenciones posibles para emails de rol se encuentra en `ia/constantes/intenciones.py`, lo que garantiza coherencia en toda la aplicación (IA, tests, validaciones).
- **Subagente de IA mejorado**:  
  El subagente principal para analizar emails (`SubagenteIntencionEmailIA`) utiliza un prompt mejorado y el perfil de IA `"clasificacion"` (temperature y top_p bajos) para respuestas más precisas y segmentadas.
- **Fallback robusto**:  
  Si la IA no detecta ninguna intención en un bloque, se clasifica automáticamente como `'otro'`, garantizando que siempre haya una intención en la respuesta.
- **Tests adaptados**:  
  Los tests de clasificación de intenciones aceptan la salida flexible de la IA y usan la lista centralizada de intenciones.
- **Configuración de depuración**:  
  Añadida configuración recomendada para depuración de tests en VS Code, incluyendo ajuste de `PYTHONPATH`.
- **Prompt de IA revisado**:  
  El prompt fuerza la segmentación por bloques/frases y exige formato JSON claro, mejorando la calidad de la respuesta de la IA.

## Estructura del proyecto
```
main.py                # Punto de entrada FastAPI
api/
  core/database.py       # Configuración de la base de datos
  models/                # Modelos SQLAlchemy (Campaign, Character, etc.)
  models/associations.py # Tablas de asociación M:N
  schemas/               # Schemas Pydantic (Create, Update, Out)
  managers/              # Lógica de negocio y orquestación
  endpoints/             # Endpoints RESTful
ia/
  langgraph/             # Sistema LangGraph para procesamiento de emails
jobs/                   # Tareas en segundo plano (cron jobs)
utils/                  # Utilidades generales (logger, loaders, etc.)
```

## Cómo ejecutar

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno:
   - Crear un archivo `.env` basado en `.env.example`.

3. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Pruebas
Asegúrate de tener la base de datos configurada y ejecuta los tests (si existen):
```powershell
pytest
```
Para depuración de tests en VS Code, asegúrate de tener el `PYTHONPATH` configurado a la raíz del proyecto en `.vscode/launch.json`.

## Endpoints principales
- `/campaigns/` — Gestión de campañas y asociación de personajes
- `/characters/` — Gestión de personajes (sin relaciones M:N en creación)
- `/story_states/` — Gestión de estados de historia y asociación de personajes
- `/scenes/`, `/turns/`, `/rulesets/`, `/players/` — Gestión de otras entidades

## Notas de arquitectura
- Las relaciones M:N (ej: personajes en campañas) se gestionan desde los endpoints de Campaign y StoryState.
- Los schemas de creación de entidades no incluyen campos de relaciones M:N.
- Actualizaciones parciales soportadas vía PATCH/PUT.
- Separación clara de lógica de negocio, acceso a datos y validación.
- El análisis de emails de rol es flexible y robusto gracias a la integración avanzada con IA.

## Linea lógica de creación de datos
- Crea el/los jugador/es (players)
- Crea el/los personaje/s (characters) y añade en formato json la hoja de personaje (hoja_json) y el estado actual (estado_actual)
- Crea la campaña y asocia los personajes a la campaña
- Crea las reglas (rulesets) y asocialas a la campaña. Luego añade los json reglas_json y contexto_json.

## TODO
- Mejorar documentación de endpoints y ejemplos de uso.
- Añadir pruebas automáticas y validación exhaustiva.
- Revisar y adaptar lógica de migraciones si es necesario.

---
Desarrollado por Francisco Javier