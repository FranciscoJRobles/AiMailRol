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

## 📂 Estructura de Archivos

```
ia/langgraph/
├── __init__.py                         # Exports principales
├── orquestador_langgraph.py           # Orquestador principal
├── ejemplos_uso.py                    # Ejemplos de uso
├── README.md                          # Esta documentación
├── graphs/                            # Grafos LangGraph
│   ├── email_processing_graph.py      # Grafo principal de emails
│   ├── combat_resolution_graph.py     # Grafo especializado en combate
├── nodes/                             # Nodos individuales del grafo
│   ├── email_analysis_node.py         # Análisis de emails con IA
│   ├── context_gathering_node.py      # Recopilación de contexto
│   ├── rules_validation_node.py       # Validación de reglas
│   ├── response_generation_node.py    # Generación de respuestas
│   ├── state_transition_node.py       # Gestión de transiciones
├── states/                            # Definiciones de estado
│   ├── email_state.py                 # Estado del procesamiento
│   ├── game_state.py                  # Estado persistente del juego
├── chains/                            # Cadenas especializadas
    ├── analysis_chain.py              # Análisis complejos
    ├── response_chain.py              # Respuestas elaboradas
├── agentes/                           # Agentes especializados
│   ├── agente_gestor_emails.py        # Gestión de emails
│   ├── agente_recopilador_contexto.py # Recopilación de contexto
│   ├── agente_resumidor_textos.py     # Resumen de textos
```

## 🔄 Flujo de Procesamiento

1. **Recopilación de Contexto**:
   - Nodo: `context_gathering_node.py`
   - Obtiene historial, resúmenes y ambientación de la campaña.

2. **Análisis de Emails**:
   - Nodo: `email_analysis_node.py`
   - Clasifica intenciones y extrae información clave.

3. **Validación de Reglas**:
   - Nodo: `rules_validation_node.py`
   - Verifica que las acciones cumplan con las reglas del juego.

4. **Generación de Respuestas**:
   - Nodo: `response_generation_node.py`
   - Genera respuestas narrativas basadas en el análisis.

5. **Transiciones de Estado**:
   - Nodo: `state_transition_node.py`
   - Actualiza el estado del juego según las acciones procesadas.

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

## 🔧 Arquitectura de Sesiones de Base de Datos

### Principio: Una Sesión por Procesamiento

**Decisión de Diseño**: Cada email se procesa con una única sesión de base de datos desde el inicio hasta el final.

#### ✅ Ventajas de esta Aproximación

1. **Consistencia Transaccional**: Todo el procesamiento es una operación lógica única
2. **Simplicidad**: Una sola responsabilidad de manejo de sesión
3. **Atomicidad**: Rollback completo si algo falla
4. **Rendimiento**: Evita overhead de crear/cerrar múltiples conexiones

#### 🔄 Flujo de Transacciones

```python
def procesar_email(self) -> Dict[str, Any]:
    db_session = SessionLocal()  # ✨ Una sesión para todo
    try:
        # 1. Buscar email pendiente
        email = EmailManager.get_next_email(db_session)
        
        # 2. Procesar con LangGraph (toda la cadena usa la misma sesión)
        result = self.email_graph.process_email(email_id, db_session, ...)
        
        # 3. Actualizar estado del juego
        if result.get('success'):
            self._update_game_state(email, result, db_session)
            db_session.commit()  # ✅ Commit si todo fue bien
        else:
            db_session.rollback()  # 🔄 Rollback si hubo error
            
    finally:
        db_session.close()  # 🔒 Siempre cerrar
```

#### 🎯 API Simplificada

**Antes** (complejo):
```python
# Múltiples opciones que complicaban el código
def procesar_email(email_id=None, db_session=None):
    # Lógica compleja para manejar diferentes combinaciones
```

**Ahora** (simple):
```python
# Una responsabilidad clara
def procesar_email(self) -> Dict[str, Any]:
    # Siempre busca el siguiente email pendiente
    # Siempre crea su propia sesión de BD
```

#### 🔄 Procesamiento en Lote

Para múltiples emails, cada uno se procesa en su propia transacción independiente:

```python
def procesar_emails_pendientes(self, max_emails=10):
    for _ in range(max_emails):
        result = self.procesar_email()  # 🔄 Cada email = nueva transacción
        if result.get('reason') == 'no_pending_emails':
            break
```

**Ventaja**: El fallo de un email no afecta el procesamiento de los demás
