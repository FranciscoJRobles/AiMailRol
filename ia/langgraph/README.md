# Sistema LangGraph para AiMailRol

Esta carpeta contiene la nueva implementación basada en **LangGraph** para el procesamiento de emails de rol narrativo. Reemplaza el sistema anterior de agentes independientes con un flujo orquestado y escalable.

## 🚀 Características Principales

- **Flujo Visual**: Grafos que muestran claramente el flujo de procesamiento
- **Estados Compartidos**: Información que persiste entre nodos del grafo
- **Paralelización**: Nodos independientes pueden ejecutarse en paralelo
- **Condicionalidad**: El grafo puede tomar rutas diferentes según el análisis
- **Especialización**: Grafos específicos para diferentes tipos de situaciones
- **Memoria**: Estados que persisten entre emails de un hilo
- **Monitoreo**: Stream de eventos para debugging y monitoreo

## 📁 Estructura de Archivos

```
ia/langgraph/
├── __init__.py                         # Exports principales
├── orquestador_langgraph.py           # Orquestador principal
├── ejemplo_uso.py                     # Ejemplos de uso
├── README.md                          # Esta documentación
├── graphs/                            # Grafos LangGraph
│   ├── email_processing_graph.py      # Grafo principal de emails
│   └── combat_resolution_graph.py     # Grafo especializado en combate
├── nodes/                             # Nodos individuales del grafo
│   ├── email_analysis_node.py         # Análisis de emails con IA
│   ├── context_gathering_node.py      # Recopilación de contexto
│   ├── rules_validation_node.py       # Validación de reglas
│   ├── response_generation_node.py    # Generación de respuestas
│   └── state_transition_node.py       # Gestión de transiciones
├── states/                            # Definiciones de estado
│   ├── email_state.py                 # Estado del procesamiento
│   └── game_state.py                  # Estado persistente del juego
└── chains/                            # Cadenas especializadas
    ├── analysis_chain.py              # Análisis complejos
    └── response_chain.py              # Respuestas elaboradas
```

## 🔄 Flujo de Procesamiento

### Grafo Principal (email_processing_graph.py)
```
[Email] → Análisis → Contexto → Validación → Respuesta → Transición → [Fin]
```

1. **Análisis**: Clasifica intenciones y detecta transiciones
2. **Contexto**: Recopila historial, reglas y estado del juego
3. **Validación**: Verifica acciones contra las reglas
4. **Respuesta**: Genera la narrativa de respuesta
5. **Transición**: Actualiza estado y persiste cambios

### Grafo de Combate (combat_resolution_graph.py)
```
[Email] → Análisis → Contexto → Iniciativa → Resolución → Respuesta → [Fin]
```

Especializado para situaciones de combate con manejo de turnos e iniciativas.

## 🛠️ Uso Básico

### Procesamiento Individual
```python
from ia.langgraph import orquestador_langgraph

# Procesar un email específico
resultado = orquestador_langgraph.procesar_email(email_id=123)
```

### Procesamiento en Lote
```python
# Procesar hasta 10 emails pendientes
resultado = orquestador_langgraph.procesar_emails_pendientes(max_emails=10)
```

### Uso Directo de Grafos
```python
from ia.langgraph import EmailProcessingGraph
from api.core.database import SessionLocal

graph = EmailProcessingGraph()
db_session = SessionLocal()

resultado = graph.process_email(
    email_id=123,
    db_session=db_session,
    current_state="narracion"
)
```

## 🎯 Estados del Sistema

### EmailState
Estado que se pasa entre nodos durante el procesamiento:
- Email original y análisis
- Contexto del juego
- Validaciones aplicadas
- Respuesta generada
- Metadatos y errores

### GameState
Estado persistente del juego entre emails:
- Estado actual (narración/combate)
- Personajes activos
- Contexto narrativo
- Información de combate
- Historial reciente

## 🔧 Integración con Sistema Existente

El nuevo sistema **reutiliza completamente** la infraestructura existente:

- **Managers**: Los nodos usan directamente `api/managers/*`
- **Modelos**: Mismas entidades de `api/models/*`
- **Schemas**: Misma validación de `api/schemas/*`
- **Base de Datos**: Misma configuración y tablas

**No hay duplicación de lógica** - solo orquestación mejorada.

## 📊 Monitoreo y Debugging

### Stream de Eventos
```python
for evento in graph.process_email_stream(email_id=123, db_session=db):
    print(f"Paso actual: {evento}")
```

### Estadísticas
```python
stats = orquestador_langgraph.get_processing_stats()
print(f"Emails pendientes: {stats['emails_pendientes']}")
```

### Visualización
```python
graph = EmailProcessingGraph()
print(graph.get_graph_visualization())
```

## 🚨 Migración desde Sistema Anterior

### En email_db_cron.py
```python
# ANTES
from ia.orquestador_ia import OrquestadorIA
OrquestadorIA.procesar_email()

# AHORA
from ia.langgraph import orquestador_langgraph
orquestador_langgraph.procesar_emails_pendientes()
```

### Ventajas de la Migración

1. **Flujo Visual**: Puedes ver exactamente qué está pasando
2. **Error Handling**: Mejor manejo de errores por nodo
3. **Paralelización**: Nodos independientes pueden ejecutarse en paralelo
4. **Especialización**: Grafos específicos para combate, narración, etc.
5. **Escalabilidad**: Fácil agregar nuevos nodos o grafos
6. **Debugging**: Stream de eventos para debugging en tiempo real
7. **Persistencia**: Estados que se mantienen entre emails

## 🔮 Extensiones Futuras

### Nuevos Grafos
- **Grafo de Exploración**: Para escenas de exploración detallada
- **Grafo Social**: Para interacciones complejas entre personajes
- **Grafo de Puzzles**: Para acertijos y desafíos mentales

### Nuevos Nodos
- **Nodo de Tiradas**: Gestión especializada de dados
- **Nodo de PNJs**: Generación dinámica de personajes
- **Nodo de Mapas**: Integración con mapas y ubicaciones

### Integraciones
- **Websockets**: Respuestas en tiempo real
- **Voice**: Respuestas por audio
- **Images**: Generación de imágenes descriptivas

## 📝 Logs y Debugging

El sistema usa logging estándar de Python:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Los logs aparecerán automáticamente durante el procesamiento
```

## 🤝 Contribución

Para agregar nuevos nodos o grafos:

1. Crear el nodo en `nodes/`
2. Agregarlo al grafo en `graphs/`
3. Actualizar estados si es necesario
4. Agregar tests y documentación

## 💡 Ejemplos Completos

Ver `ejemplo_uso.py` para ejemplos detallados de todas las funcionalidades.
