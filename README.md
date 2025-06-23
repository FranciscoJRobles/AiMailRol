# AiMailRol Backend

Backend para un sistema de rol multijugador por email, con integración de IA y arquitectura moderna basada en FastAPI y SQLAlchemy. Permite la gestión flexible de campañas, subtramas, escenas, personajes y turnos, soportando relaciones complejas y actualizaciones parciales.

## Características principales
- **FastAPI** para endpoints RESTful modernos y documentación automática.
- **SQLAlchemy** para ORM y gestión de relaciones 1:N y M:N entre entidades.
- **Pydantic** para validación de datos y schemas de entrada/salida.
- **Integración con IA** para automatización y generación de contenido.
- **Gestión de campañas, personajes, escenas, turnos, reglas y estados de historia**.
- **Actualizaciones parciales (PATCH/PUT)** y endpoints para asociar/desasociar entidades.
- **Separación clara de modelos, schemas, crud, managers y endpoints**.

## Estructura del proyecto
```
api/
  main.py                # Punto de entrada FastAPI
  core/database.py       # Configuración de la base de datos
  models/                # Modelos SQLAlchemy (Campaign, Character, etc.)
  models/associations.py # Tablas de asociación M:N
  schemas/               # Schemas Pydantic (Create, Update, Out)
  crud/                  # Lógica CRUD para cada entidad
  managers/              # Lógica de negocio y orquestación
  endpoints/             # Rutas y controladores FastAPI
config/
  credentials.json, token.json # Configuración de servicios externos
ia/
  ia_client.py           # Cliente para integración de IA
jobs/
  email_cron.py          # Tareas programadas (cron)
services/
  gmail_service.py, ...  # Servicios externos y utilidades
utils/
  env_loader.py          # Utilidades de entorno
```

## Instalación
1. Clona el repositorio y accede al directorio:
   ```powershell
   git clone <repo-url>
   cd AiMailRol
   ```
2. Instala las dependencias:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno y archivos en `config/` según sea necesario.

## Ejecución
Lanza el servidor de desarrollo con:
```powershell
uvicorn api.main:app --reload
```
Accede a la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs)

## Pruebas
Asegúrate de tener la base de datos configurada y ejecuta los tests (si existen):
```powershell
pytest
```

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

## TODO
- Mejorar documentación de endpoints y ejemplos de uso.
- Añadir pruebas automáticas y validación exhaustiva.
- Revisar y adaptar lógica de migraciones si es necesario.

---
Desarrollado por Francisco Javier Robles de Toro.
