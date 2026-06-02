# Módulo: a_00_config.py — Configuración Central del Sistema de Trazabilidad

## Responsabilidad del módulo

Este módulo define la configuración global del sistema de trazabilidad de stock. Centraliza constantes, reglas de negocio, umbrales numéricos, categorías de movimientos y modos operativos del sistema.

Su función es actuar como **fuente única de verdad (single source of truth)** para parámetros críticos utilizados en el análisis, reconstrucción y validación del stock.

---

## Problema que resuelve dentro del sistema

En un sistema de trazabilidad de stock con múltiples fuentes de movimientos (ventas, compras, ajustes, conteos), la lógica de interpretación puede volverse inconsistente si cada módulo define sus propias reglas.

Este módulo resuelve:

- Inconsistencias en interpretación de movimientos
- Falta de estandarización de tolerancias numéricas
- Dificultad para ajustar comportamiento del sistema sin tocar lógica interna
- Dispersión de reglas de negocio en múltiples archivos

---

## Entradas (inputs)

Este módulo no recibe entradas dinámicas en tiempo de ejecución.

Sus “inputs” conceptuales son:

- Reglas de negocio del dominio (definidas por el usuario del sistema)
- Parámetros de configuración del entorno (DB, fechas, modos)
- Clasificación de tipos de movimientos del sistema

---

## Salidas (outputs)

El módulo expone constantes globales utilizadas por:

- Motor de trazabilidad
- Reconstructores de stock
- Analizadores de errores
- Generadores de reportes

Outputs principales:

- Configuración de base de datos
- Fechas de referencia
- Umbrales de tolerancia numérica
- Clasificación de movimientos (suma, resta, reseteo)
- Prioridades de interpretación
- Flags de comportamiento del sistema

---

## Funciones principales

Este módulo no contiene funciones ejecutables. Su lógica es declarativa.

Sin embargo, sus componentes clave son:

- Configuración de base de datos: define el archivo principal del sistema.
- Parámetros de tolerancia: controlan precisión y detección de ruido.
- Reglas de movimientos: determinan cómo cada evento afecta el stock.
- Reglas de reseteo: definen eventos que reinician o reestructuran el cálculo del stock.
- Reglas de prioridad: establecen jerarquía en conflictos de interpretación.
- Modos del sistema: controlan comportamiento global (debug, automatización, exportación).

---

## Dependencias con otros módulos

Este módulo es consumido por prácticamente todo el sistema de trazabilidad, especialmente:

- Motor de reconstrucción de stock
- Analizador de inconsistencias
- Procesador de movimientos históricos
- Generador de reportes Excel
- Validadores de coherencia de datos
- Módulos de auditoría

No depende de ningún otro módulo del sistema.

---

## Flujo lógico general

1. El sistema inicia y carga este módulo como base de configuración.
2. Los módulos de procesamiento leen estas constantes.
3. Cada evento de movimiento es interpretado según las reglas definidas aquí.
4. Los umbrales numéricos se aplican para filtrar ruido o inconsistencias.
5. La clasificación de movimientos determina cómo se modifica el stock.
6. Los modos del sistema ajustan el comportamiento global (debug, automatización, exportación).

---

## Casos críticos o riesgos

- **Cambios en reglas de movimientos**: pueden alterar completamente la reconstrucción histórica del stock.
- **Tolerancias mal ajustadas**: pueden generar falsos positivos o pérdida de precisión en trazabilidad.
- **Clasificación incorrecta de movimientos**: impacta directamente en saldos y auditoría.
- **Dependencia global**: cualquier error aquí se propaga a todo el sistema.
- **Falta de versionado de configuración**: dificulta reproducir resultados históricos.

---

## Interacción con el sistema de trazabilidad

Este módulo actúa como núcleo de parametrización del sistema completo:

- El motor de reconstrucción consulta reglas para sumar/restar/resetear stock.
- El analizador de errores usa umbrales para detectar inconsistencias.
- Los reportes dependen de flags como `GENERAR_EXCEL`.
- El sistema de auditoría se apoya en la clasificación de movimientos.
- Los módulos de conteo y ajuste utilizan reglas específicas de reseteo.

En términos arquitectónicos, este módulo funciona como una **capa de configuración transversal**, sin lógica operativa propia pero con impacto directo en todos los procesos del sistema.

---









# Módulo: a_db.py — Capa de Acceso a Base de Datos

## Responsabilidad del módulo
Este módulo implementa una capa básica de acceso y control de la base de datos SQLite del sistema. Su responsabilidad es centralizar la conexión, ejecución de consultas y commits, proporcionando una interfaz mínima reutilizable para el resto del sistema.

Actúa como punto único de interacción con la base de datos interna, evitando que otros módulos gestionen conexiones directamente.

---

## Problema que resuelve dentro del sistema
Resuelve la necesidad de:

- Evitar conexiones dispersas a SQLite en múltiples módulos
- Centralizar la ejecución de queries SQL
- Simplificar el acceso a datos mediante una instancia global reutilizable
- Reducir duplicación de código relacionado con conexión y cursor
- Facilitar el mantenimiento del acceso a datos en todo el sistema POS

---

## Entradas (inputs)
- Sentencias SQL en formato string
- Parámetros opcionales en forma de tuplas (`params`)
- Llamadas a métodos de control de conexión (`conectar`, `commit`, `cerrar`)

---

## Salidas (outputs)
- Resultados de consultas SQL:
  - Listas de filas (`fetchall`)
  - Una sola fila (`fetchone`)
- Estado persistido en la base de datos tras `commit()`
- Conexión activa a SQLite (`sqlite3.Connection`)
- Cursor activo (`sqlite3.Cursor`)

---

## Funciones principales

### `conectar()`
Establece la conexión con la base de datos si aún no existe. Inicializa cursor y configura el formato de retorno de filas.

### `ejecutar(query, params)`
Ejecuta una consulta SQL y devuelve múltiples resultados. No realiza commit automático.

### `ejecutar_uno(query, params)`
Ejecuta una consulta SQL y devuelve un único registro.

### `commit()`
Confirma transacciones pendientes en la base de datos.

### `cerrar()`
Cierra la conexión activa y libera recursos del cursor.

---

## Dependencias con otros módulos
- `sqlite3` (librería estándar)
- `a_00_config` (importado aunque no se utiliza directamente en este módulo)
- Módulos del sistema POS que consumen `db` como instancia global

---

## Flujo lógico general
1. Un módulo del sistema solicita acceso a datos mediante `db.ejecutar()` o `db.ejecutar_uno()`
2. Si no existe conexión activa, se crea automáticamente
3. Se ejecuta la consulta SQL con parámetros opcionales
4. Se devuelven los resultados sin persistir cambios
5. Si hubo modificaciones, el módulo consumidor ejecuta `db.commit()`
6. La conexión puede mantenerse abierta durante toda la sesión o cerrarse explícitamente

---

## Casos críticos o riesgos
- **Persistencia de conexión global**: el uso de una instancia global puede generar estados compartidos no controlados en sistemas concurrentes
- **Falta de manejo de errores**: no hay captura de excepciones SQL, lo que puede interrumpir el flujo del sistema
- **Commit manual obligatorio**: riesgo de olvidos que provoquen pérdida de cambios
- **Reutilización de cursor global**: puede generar comportamientos inesperados si múltiples módulos ejecutan consultas simultáneamente
- **Dependencia implícita de estado interno** (`conn` y `cursor`)

---

## Interacción con el sistema de trazabilidad de stock
Este módulo actúa como base de persistencia para todo el sistema de trazabilidad.

Es utilizado indirectamente por:

- Módulos de stock (movimientos, ajustes, reconstrucción)
- Módulos de ventas y compras
- Módulos de reportes históricos
- Módulos de auditoría y seguimiento

En el sistema de trazabilidad, su rol es crítico porque:

- Garantiza el acceso consistente a los eventos de stock almacenados
- Permite reconstrucción histórica mediante consultas SQL
- Soporta la integridad de datos que alimentan el simulador y el reconstructor
- Funciona como capa inferior de toda la cadena de eventos del sistema

---

## Observación arquitectónica
Este módulo cumple una función de “mini ORM manual”, aunque sin abstracciones avanzadas. Es funcional y liviano, pero en sistemas de mayor escala podría evolucionar hacia:

- Context managers (`with`)
- Manejo de transacciones explícitas
- Capa de repositorios por entidad
- Control de concurrencia más robusto



















# b_loader_movimientos.py — Módulo de Carga Unificada de Movimientos

## Responsabilidad del módulo

Este módulo es responsable de **construir una línea de tiempo unificada de eventos de stock** para un producto específico, consolidando información proveniente de múltiples fuentes del sistema (ventas, compras, historial de stock, conteos físicos y promociones).

Su función principal es actuar como **capa de extracción y normalización de datos (ETL inicial)** para el motor de trazabilidad.

---

## Problema que resuelve dentro del sistema

El sistema POS almacena los movimientos de stock en tablas separadas y con estructuras heterogéneas. Esto genera:

- Fragmentación de la información
- Dificultad para reconstruir el estado real del stock
- Inconsistencias entre ventas, compras y ajustes manuales
- Falta de un orden cronológico coherente de eventos

Este módulo resuelve ese problema generando una **fuente única de eventos ordenados temporalmente**, lista para ser procesada por el motor de reconstrucción de stock.

---

## Entradas (inputs)

### Parámetros de función
- `codigo_producto`: Identificador del producto a analizar
- `fecha_inicio`: Fecha mínima desde la cual se consideran eventos
- `fecha_fin` (opcional): reservado para futuras extensiones (actualmente no aplicado)

### Fuentes de datos (base de datos)
- `historial_de_articulos`
- `facturas_detalladas`
- `facturas_resumidas`
- `conteo_de_stock`
- `ventas_detalladas`
- `ventas_resumidas`
- `promociones`

---

## Salidas (outputs)

Retorna una **lista de eventos normalizados**, donde cada evento contiene:

- fecha del movimiento
- tipo de evento (venta, compra, conteo, historial, factura_resumida)
- descripción del movimiento
- valores de stock (cuando aplica)
- cantidad afectada
- referencias opcionales (factura, etc.)

Esta salida es consumida directamente por el motor de trazabilidad.

---

## Funciones principales

### `cargar_eventos(codigo_producto, fecha_inicio, fecha_fin)`
Función central del módulo. Extrae, normaliza y unifica todos los movimientos del producto desde distintas fuentes.

### `obtener_eventos(codigo_producto, fecha_inicio, fecha_fin)`
Wrapper público que expone la API del módulo y delega en `cargar_eventos`.

### `parse_fecha(fecha)`
Utilidad interna para convertir strings de fecha a objetos datetime para ordenamiento consistente.

---

## Dependencias con otros módulos

- `a_db`: acceso a base de datos (capa de persistencia)
- `a_00_config`: configuración global del sistema (fechas base, prioridades)

---

## Flujo lógico general

1. Conexión a la base de datos
2. Extracción de eventos desde múltiples tablas:
   - Historial de stock (ajustes manuales o automáticos)
   - Compras (facturas detalladas)
   - Agrupación de facturas (resumidas)
   - Conteos físicos de stock
   - Ventas (incluyendo promociones)
3. Normalización de cada fuente a un formato común de evento
4. Conversión de cantidades según tipo de operación
5. Unificación de todos los eventos en una sola lista
6. Ordenamiento cronológico por:
   - Fecha del evento
   - Prioridad del tipo de movimiento
7. Retorno de la lista consolidada

---

## Casos críticos o riesgos

### 1. Falta de uso de `fecha_fin`
Actualmente el filtro temporal no es bidireccional, lo que puede generar sobrecarga de datos innecesarios.

### 2. Dependencia fuerte en integridad de datos
Errores en tablas como promociones o facturas pueden distorsionar completamente la reconstrucción.

### 3. Ambigüedad en historial de stock
El campo `desde` no siempre es estructurado, lo que puede afectar análisis posteriores.

### 4. Crecimiento de volumen
El módulo no implementa optimización para grandes datasets (posible impacto en performance).

### 5. Ordenamiento basado en parsing repetido de fechas
Puede generar costo innecesario en escenarios de alta carga.

---

## Interacción con el sistema de trazabilidad

Este módulo es el **primer eslabón del pipeline de reconstrucción de stock**.

Flujo típico del sistema:

1. `b_loader_movimientos.py`
   → genera eventos unificados

2. `c_motor_trazabilidad.py`
   → reconstruye el stock en base a esos eventos

3. `d_analizador_errores.py`
   → detecta inconsistencias en la reconstrucción

4. `e_sugeridor_correcciones.py`
   → propone correcciones sobre datos inconsistentes

5. `i_simulador.py`
   → simula escenarios completos del stock

---

## Rol arquitectónico dentro del sistema

Este módulo actúa como:

- **Capa de extracción de datos (Data Ingestion)**
- **Normalizador de fuentes heterogéneas**
- **Base del modelo temporal del sistema**
- **Punto de entrada del motor de trazabilidad**

Su calidad impacta directamente en la precisión de toda la reconstrucción del stock.

---









# c_motor_trazabilidad.py

## Responsabilidad del módulo

Este módulo implementa el **motor central de reconstrucción de stock histórico** dentro del sistema de trazabilidad. Su función es calcular el estado del stock de un producto a lo largo del tiempo a partir de eventos de movimientos, aplicando reglas de negocio específicas (sumas, restas, conteos directos y reinicios de valor).

Además, incorpora una capa básica de **detección de inconsistencias** en la evolución del stock reconstruido.

---

## Problema que resuelve dentro del sistema

En sistemas de inventario con múltiples fuentes de movimiento (ventas, compras, ajustes, conteos físicos, etc.), el stock real no puede inferirse directamente desde un valor único en base de datos.

Este módulo resuelve:

- Reconstrucción del stock histórico de un producto a partir de eventos heterogéneos
- Corrección implícita de inconsistencias en la secuencia de movimientos
- Determinación de un estado de stock coherente en el tiempo
- Detección de saltos anómalos en la evolución del inventario

---

## Entradas (inputs)

- `codigo_producto`: Identificador del producto a analizar
- `fecha_inicio` (opcional): Punto temporal desde el cual se reconstruye el historial (default configurable)
- Eventos obtenidos desde capa de datos:
  - `movimiento`
  - `cantidad`
  - `valor_anterior`
  - `nuevo_valor`
  - `comentario`
  - `fecha_carga`, `fecha_compra`

---

## Salidas (outputs)

### Función `reconstruir_stock`
- Lista de eventos enriquecidos con:
  - `stock_reconstruido`: estado del stock luego de cada evento
  - Campos originales preservados

### Función `detectar_inconsistencias`
- Lista de eventos considerados anómalos por saltos excesivos en el stock

### Función `analizar`
- Diccionario estructurado:
  - `historial`: evolución completa del stock
  - `errores`: inconsistencias detectadas

---

## Funciones principales

- **`reconstruir_stock`**  
  Motor principal de trazabilidad. Recorre los eventos cronológicamente y calcula el stock acumulado aplicando reglas de negocio según tipo de movimiento.

- **`consigue_stock_base_y_inicio`**  
  Determina el stock inicial confiable y el punto de arranque efectivo del análisis, combinando conteos físicos, ajustes y acumulación de ventas previas.

- **`detectar_inconsistencias`**  
  Analiza saltos abruptos entre estados consecutivos de stock reconstruido para identificar posibles errores de carga o lógica.

- **`analizar`**  
  API de alto nivel que encapsula reconstrucción + validación de inconsistencias.

---

## Dependencias con otros módulos

- `b_loader_movimientos` → fuente de eventos históricos (`obtener_eventos`)
- `a_00_config` → constantes de configuración (reglas de movimientos, umbrales, fechas base)
- `a_db` → acceso a datos del sistema
- `datetime` → normalización de fechas
- `copy` → aislamiento de estructuras para evitar mutaciones

---

## Flujo lógico general

1. Se consultan los eventos del producto desde la capa de datos
2. Se normalizan y ordenan implícitamente mediante procesamiento secuencial
3. Se calcula un **stock base inicial confiable**
   - Basado en conteos directos, resets o acumulación de ventas previas
4. Se recorre el historial completo de eventos:
   - Cada tipo de movimiento modifica el stock según reglas definidas
5. Se genera una versión enriquecida del historial con stock reconstruido
6. Se ejecuta análisis de consistencia entre estados consecutivos
7. Se retorna estructura final con historial + errores

---

## Casos críticos o riesgos

- **Dependencia fuerte en clasificación de movimientos**  
  Un error en las categorías de `MOVIMIENTOS_*` afecta completamente la reconstrucción.

- **Eventos fuera de orden temporal**  
  El modelo asume consistencia temporal; desorden puede generar stock inválido.

- **Conteos físicos como puntos de reinicio**  
  Si un conteo directo es incorrecto, contamina toda la línea histórica posterior.

- **Acumulación de errores silenciosos**  
  Algunas conversiones fallidas de datos numéricos son ignoradas sin interrupción del flujo.

- **Saltos grandes no siempre indican error real**  
  La heurística de inconsistencias puede generar falsos positivos en ajustes legítimos.

---

## Interacción con el sistema de trazabilidad

Este módulo es el **núcleo del pipeline de trazabilidad**, y actúa como punto central entre:

- **Ingreso de datos** (movimientos desde base de datos)
- **Análisis de errores** (consumido por módulos de diagnóstico)
- **Corrección de inconsistencias** (módulos posteriores de sugerencia o reparación)
- **Reportes y visualización** (interfaces que muestran evolución del stock)

Su salida alimenta directamente:
- motores de análisis de errores
- sistemas de auditoría
- herramientas de reconstrucción y validación
- reportes históricos de stock

---

## Rol dentro de la arquitectura

Funciona como un **motor determinístico de reconstrucción de estado**, convirtiendo eventos dispersos en una serie temporal coherente de inventario, que luego es utilizada como base para análisis superiores del sistema.









# Módulo: d_analizador_errores.py  
## Analizador de consistencia y detección de anomalías en trazabilidad de stock

---

## 1. Responsabilidad del módulo

Este módulo se encarga de analizar un historial de movimientos de stock reconstruido y detectar inconsistencias, errores lógicos y anomalías en la trazabilidad.

Su objetivo principal es validar la coherencia histórica del stock calculado frente a las reglas del sistema, identificando desviaciones, saltos inesperados y fallos de consistencia en los movimientos registrados.

---

## 2. Problema que resuelve dentro del sistema

En un sistema de trazabilidad de stock, los datos pueden presentar inconsistencias debido a:

- errores de carga de datos históricos  
- movimientos desordenados temporalmente  
- reconstrucción incorrecta del stock  
- fallos en conteos o facturación  
- discrepancias entre valor anterior y stock reconstruido  

Este módulo resuelve la necesidad de:

- detectar errores no evidentes en cálculos de stock  
- validar integridad histórica del movimiento de inventario  
- identificar inconsistencias entre eventos consecutivos  
- separar falsos positivos mediante reglas de negocio  

---

## 3. Entradas (inputs)

- `historial` (list[dict])  
  Lista de eventos de movimientos de stock ya reconstruidos.

Cada registro puede incluir:
- movimiento
- stock_reconstruido
- valor_anterior
- nuevo_valor
- cantidad
- otros campos de auditoría

---

## 4. Salidas (outputs)

El módulo devuelve estructuras de análisis con:

### Salida principal (`ejecutar_analisis`)
Diccionario con:

- `errores`: lista completa de anomalías detectadas  
- `total_errores`: cantidad total de errores  
- `inconsistencias`: subconjunto de inconsistencias históricas reales  
- `total_inconsistencias`: total de inconsistencias críticas  
- `resumen`: conteo agrupado por tipo de error  

---

## 5. Funciones principales

### Validación y utilidades
- `es_valido_numero(x)`  
  Valida si un valor puede interpretarse como número válido.

- `norm(x)`  
  Normaliza cadenas para comparación (lower + strip).

- `normalizar(x)`  
  Convierte valores a float de forma segura.

- `coincide_con_tolerancia(a, b)`  
  Compara valores numéricos considerando tolerancia absoluta y redondeo.

---

### Núcleo de análisis

- `analizar_errores(historial)`  
  Motor principal de detección de inconsistencias.  
  Recorre el historial y aplica reglas de validación, incluyendo:
  - saltos de stock excesivos  
  - valores nulos críticos  
  - inconsistencias históricas de valor anterior  
  - validaciones específicas por tipo de movimiento  
  - filtros de falsos positivos  

---

### Agregación

- `resumir_errores(errores)`  
  Agrupa errores por tipo para análisis estadístico.

---

### API del módulo

- `ejecutar_analisis(historial)`  
  Interfaz principal del módulo.  
  Ejecuta el análisis completo y devuelve resultados estructurados listos para consumo por otros módulos.

---

## 6. Dependencias con otros módulos

- `a_00_config`  
  Provee constantes críticas:
  - tolerancias numéricas  
  - movimientos ignorados  
  - umbrales de salto permitido  

- `copy.deepcopy`  
  Garantiza que el historial original no sea mutado durante el análisis.

---

## 7. Flujo lógico general

1. Se recibe el historial reconstruido de stock  
2. Se crea una copia segura de los datos  
3. Se recorre secuencialmente cada evento  
4. Se normalizan valores numéricos y de texto  
5. Se aplican reglas de filtrado por tipo de movimiento  
6. Se validan:
   - valores nulos  
   - saltos de stock  
   - coherencia con valores anteriores esperados  
   - consistencia histórica con referencias pasadas  
7. Se aplican filtros de falsos positivos por patrones conocidos  
8. Se registran errores detectados  
9. Se genera resumen agregado  
10. Se devuelve resultado estructurado

---

## 8. Casos críticos o riesgos

- **Falsos positivos complejos**  
  Los filtros dependen de patrones de negocio que pueden cambiar.

- **Dependencia fuerte del orden del historial**  
  El análisis asume orden cronológico implícito.

- **Sensibilidad a tolerancias numéricas**  
  Ajustes en `TOLERANCIA_NUMERICA` pueden alterar significativamente los resultados.

- **Ambigüedad en reconstrucción de stock**  
  Si el historial ya viene corrupto, el análisis puede propagar supuestos erróneos.

- **Movimientos ignorados**  
  Cambios en `MOVIMIENTOS_IGNORE` pueden alterar el diagnóstico global.

---

## 9. Integración con el sistema de trazabilidad

Este módulo se ubica en la capa de auditoría lógica del sistema POS y se integra como:

- consumidor de datos del sistema de reconstrucción de stock  
- validador posterior al procesamiento de movimientos  
- generador de alertas para revisión manual o automática  
- insumo para reportes de integridad de inventario  

Interactúa indirectamente con:

- módulos de reconstrucción de stock  
- módulos de carga de facturas y ventas  
- sistemas de conteo físico  
- herramientas de reportes y auditoría  

---

## 10. Rol dentro de la arquitectura

Este módulo actúa como un **filtro de consistencia avanzada**, ubicado entre:

- la reconstrucción de datos históricos  
- y la capa de reportes / decisiones operativas  

Su función no es corregir datos, sino **detectar y clasificar anomalías estructurales** en la trazabilidad del inventario.









# e_sugeridor_correcciones.py

## 🧭 Responsabilidad del módulo

Este módulo se encarga de analizar historiales de stock reconstruido para detectar inconsistencias críticas (principalmente tramos de stock negativo) y generar sugerencias de corrección basadas en la simulación de eventos futuros.

Su función no es corregir automáticamente, sino **proponer acciones correctivas trazables y justificadas** dentro del flujo de auditoría del sistema de stock.

---

## 🎯 Problema que resuelve dentro del sistema

En el sistema de trazabilidad de stock pueden aparecer inconsistencias por:

- Desorden temporal en eventos
- Movimientos mal registrados o fuera de secuencia
- Facturas o entradas aplicadas en fechas incorrectas
- Conteos o resets que distorsionan el flujo real del stock

Este módulo aborda el problema de:

> Detectar tramos donde el stock reconstruido cae en valores inválidos (negativos o fuera de tolerancia) y proponer hipótesis de corrección basadas en eventos posteriores.

---

## 📥 Entradas (inputs)

- `historial` (list[dict])
  - Lista cronológica de eventos de stock reconstruido
  - Cada evento puede contener:
    - `fecha`
    - `movimiento`
    - `stock_reconstruido`
    - `cantidad`
    - `nuevo_valor`
    - `valor_anterior`
    - `id_factura`

---

## 📤 Salidas (outputs)

Retorna un diccionario con:

- `total_sugerencias` (int)
- `sugerencias` (list[dict])

Cada sugerencia puede ser:

### Tipos principales:
- `mover_factura`
- `ajuste_requerido`
- `revision_manual`

### Campos típicos:
- contexto del tramo negativo
- evento origen
- evento candidato a corrección
- fecha sugerida de ajuste
- valores de stock involucrados
- prioridad de corrección

---

## ⚙️ Funciones principales

### `detectar_tramos_negativos()`
Identifica segmentos del historial donde el stock cae por debajo del umbral definido.

---

### `buscar_ultimo_positivo()`
Localiza el último estado confiable de stock antes del inicio del tramo problemático.

---

### `es_movimiento_entrada()`
Determina si un movimiento representa ingreso de stock al sistema.

---

### `sugerir_correcciones()`
Motor principal del módulo.
- Simula evolución del stock hacia adelante
- Evalúa eventos posteriores al error
- Genera hipótesis de corrección
- Clasifica sugerencias según impacto

---

### `ejecutar_sugerencias()`
API pública del módulo.
Devuelve estructura final lista para consumo por otros módulos.

---

## 🔗 Dependencias con otros módulos

- `a_00_config`
  - Umbrales de tolerancia
  - Tipos de movimientos válidos
- `datetime`
  - Análisis temporal de eventos
- `copy.deepcopy`
  - Aislamiento del historial original

---

## 🔄 Flujo lógico general

1. Recepción del historial de stock reconstruido
2. Detección de tramos negativos o inválidos
3. Identificación del último estado confiable previo
4. Simulación de evolución del stock desde el punto crítico
5. Evaluación de eventos futuros relevantes
6. Generación de sugerencias de corrección
7. Clasificación por tipo y prioridad
8. Retorno estructurado del análisis

---

## ⚠️ Casos críticos o riesgos

- Dependencia fuerte del orden cronológico del historial
- Sensibilidad a inconsistencias en `MOVIMIENTOS_RESETEO`
- Interpretación ambigua de signos en cantidades de entrada/salida
- Posible subdetección de errores si el stock virtual no cruza umbrales
- Alta dependencia de tolerancias configuradas externamente

---

## 🧩 Interacción con el sistema de trazabilidad

Este módulo se sitúa en la capa de **análisis inteligente posterior a la reconstrucción de stock**.

Interactúa indirectamente con:

- Motor de reconstrucción de stock (fuente del historial)
- Analizador de errores (consumidor de sugerencias)
- Sistema de aplicación de correcciones (ejecutor potencial de sugerencias)
- Reportes de auditoría y trazabilidad

Su rol es el de **generador de hipótesis de corrección dentro del pipeline de auditoría**, no de modificación directa del sistema.

---

## 📌 Nota arquitectónica

Este módulo funciona como una capa de inferencia heurística dentro del sistema de trazabilidad. Su valor depende de la calidad del historial reconstruido y de la consistencia de los eventos temporales del sistema.









# f_aplicador_cambios.py

## 1. Responsabilidad del módulo

Este módulo es el encargado de **aplicar cambios estructurales en la línea de tiempo de eventos del sistema de trazabilidad**, específicamente cuando se requiere **reubicar facturas en el tiempo** y mantener la coherencia del historial de stock asociado.

Su función central es asegurar que, ante una modificación temporal de una factura, el sistema:

- Recalcule el impacto de esa factura en el stock.
- Reordene los eventos históricos asociados.
- Persista un historial reconstruido consistente.
- Actualice el stock actual derivado del nuevo orden temporal.

---

## 2. Problema que resuelve dentro del sistema

En sistemas de trazabilidad de stock, mover una factura en el tiempo genera inconsistencias graves:

- El stock histórico queda desfasado.
- Los eventos no respetan el orden cronológico real.
- El stock actual puede quedar incorrecto.
- El historial deja de ser determinístico.

Este módulo resuelve el problema de:

> **Reescritura consistente del historial de stock cuando se modifica la fecha de eventos de compra (facturas).**

---

## 3. Entradas (inputs)

### Entrada principal:
- `cambios` (lista de diccionarios)

### Estructura esperada de cada cambio:
- `tipo`: tipo de operación (ej. `"mover_factura"`)
- `id_factura`: identificador de la factura
- `fecha_sugerida`: nueva fecha/hora destino

### Dependencias de base de datos:
- `facturas_resumidas`
- `facturas_detalladas`
- `historial_de_articulos`
- `productos`

---

## 4. Salidas (outputs)

### Persistencia en base de datos:
- Actualización de fechas en:
  - facturas
  - detalles de factura
  - historial de artículos
- Reescritura de valores:
  - `valor_anterior`
  - `nuevo_valor`
- Actualización de:
  - `stock_actual` en productos

### Efectos secundarios:
- Historial de trazabilidad reconstruido y corregido
- Stock recalculado según nueva cronología
- Logs de auditoría por consola

---

## 5. Funciones principales

### `aplicar_cambios(cambios)`
Orquestador principal del módulo. Ejecuta el flujo completo de modificación temporal de facturas y disparo de reconstrucción de stock.

---

### `reconstruir_y_persistir_historial(conn, codigo_producto, fecha_inicio, ts_old_str)`
- Reconstruye el historial de un producto desde un punto temporal.
- Ajusta valores históricos calculados.
- Persiste correcciones en `historial_de_articulos`.

---

### `actualizar_stock_actual_desde_historial(conn, codigo_producto)`
- Deriva el stock final del producto desde el historial reconstruido.
- Actualiza el valor actual en tabla `productos`.

---

### `parse_dt(s)`
Convierte string de fecha a objeto datetime.

---

### `fmt_dt(dt)`
Convierte datetime a string estándar del sistema.

---

## 6. Dependencias con otros módulos

### Internas del sistema POS/trazabilidad:
- `a_db` → conexión y cursor de base de datos
- `j_reconstructor` → motor de reconstrucción histórica de stock
- `a_00_config` → constantes del sistema (fechas base, configuración global)

### Dependencias conceptuales:
- Motor de trazabilidad de eventos
- Sistema de facturación histórica
- Modelo de stock basado en eventos

---

## 7. Flujo lógico general

1. Recepción de cambios tipo `"mover_factura"`.
2. Obtención de factura original (fecha + proveedor).
3. Cálculo del offset temporal entre fecha original y nueva.
4. Reubicación temporal de:
   - factura
   - detalles
   - eventos de historial asociados
5. Identificación de productos afectados.
6. Para cada producto:
   - Determinación de punto mínimo de reconstrucción.
   - Reconstrucción del historial desde ese punto.
   - Persistencia de valores recalculados.
   - Actualización del stock final.
7. Commit de transacción global.

---

## 8. Casos críticos o riesgos

### 1. Inconsistencia temporal parcial
Si falla la reconstrucción en un producto, puede quedar:
- historial parcialmente actualizado
- stock desalineado

---

### 2. Colisiones de timestamps
El sistema depende de igualdad exacta en:
- `fecha_y_hora_de_modificacion`
Pequeñas diferencias pueden romper el update del historial.

---

### 3. Dependencia fuerte del reconstructor
El módulo depende críticamente de:
- `reconstruir_producto`
Si este motor falla o cambia lógica, el aplicador pierde validez.

---

### 4. Operaciones destructivas
Este módulo:
- reescribe historial
- modifica fechas históricas
- recalcula stock base

Por lo tanto es **altamente sensible a errores de ejecución**.

---

## 9. Interacción con el sistema de trazabilidad

Este módulo actúa como una **capa de corrección temporal sobre el sistema de trazabilidad**, interfiriendo directamente en tres niveles:

### Nivel 1: Eventos (facturas y detalles)
- Reordena la cronología de entrada de datos.

### Nivel 2: Historial de artículos
- Recalcula valores derivados (stock anterior/nuevo).

### Nivel 3: Stock actual
- Reestablece consistencia final del estado del sistema.

---

## 10. Rol dentro de la arquitectura

Este módulo funciona como un:

> **Motor de reescritura histórica controlada**

Su propósito no es registrar eventos, sino **corregir la historia del sistema cuando la línea temporal se modifica**.

---









# g_reportes.py — Módulo de Reportes y Comparación de Trazabilidad

## 1. Responsabilidad del módulo

Este módulo centraliza la **generación de reportes, análisis comparativo y ejecución de pipelines de validación** sobre el sistema de trazabilidad de stock.

Actúa como una capa de **orquestación superior**, que consume resultados del motor de análisis y los transforma en:

- Reportes operativos (simples y masivos)
- Comparaciones de estado antes/después de cambios
- Flujos controlados de simulación y aplicación de modificaciones

---

## 2. Problema que resuelve dentro del sistema

El módulo resuelve la necesidad de:

- Visualizar el estado de trazabilidad de un producto de forma estructurada
- Comparar el impacto de cambios en el historial de stock
- Detectar mejoras o empeoramientos en errores y sugerencias
- Ejecutar análisis masivos sin intervención manual por producto
- Validar pipelines de corrección antes de aplicar cambios reales

En resumen, transforma el análisis técnico en **información operativa y accionable**.

---

## 3. Entradas (inputs)

El módulo recibe principalmente:

- `codigo_producto` (str): identificador del producto a analizar
- `lista_codigos` (list[str]): conjunto de productos para análisis masivo
- `historial` (list/dict): provisto indirectamente por el motor de trazabilidad
- `cambios` (estructura variable): instrucciones de modificación externa
- `aplicar_cambios_fn` (callable): función externa para aplicar cambios al sistema
- `aplicar` / `modo_simulacion` (bool): control de ejecución segura

---

## 4. Salidas (outputs)

Dependiendo del flujo ejecutado, el módulo puede devolver:

- Reportes estructurados por producto:
  - historial
  - errores detectados
  - sugerencias generadas

- Comparaciones:
  - cantidad de errores antes/después
  - diferencias netas
  - nuevos errores
  - errores resueltos
  - evaluación global (mejoró / empeoró / igual)

- Reportes masivos:
  - segmentación de productos con/sin errores
  - segmentación con/sin sugerencias

- Resultados de pipeline:
  - snapshot antes/después
  - impacto de cambios aplicados
  - comparación de ambos estados

---

## 5. Funciones principales

### `reporte_simple(codigo_producto)`
Genera un resumen operativo del estado actual del producto, incluyendo errores, sugerencias y clasificación por tipo.

---

### `reporte_completo(codigo_producto, aplicar_cambios_fn, cambios, aplicar)`
Ejecuta un análisis antes y después de aplicar cambios, y compara ambos estados para evaluar impacto.

---

### `comparar_errores(errores_antes, errores_despues)`
Calcula diferencias estructurales entre dos estados de errores:
- nuevos errores
- errores resueltos
- variación total
- agrupación por tipo

---

### `imprimir_comparacion(resultado)`
Renderiza en consola una comparación estructurada del estado del sistema.

---

### `reporte_masivo(lista_codigos)`
Ejecuta análisis batch sobre múltiples productos, clasificando cada uno según su estado de errores y sugerencias.

---

### `snapshot(codigo)`
Obtiene una captura consistente del estado actual del sistema para un producto (historial + análisis + sugerencias).

---

### `ejecutar_pipeline(...)`
Orquesta un flujo completo de validación:
1. Snapshot inicial
2. Aplicación opcional de cambios
3. Snapshot posterior
4. Comparación de estados
5. Evaluación del impacto

Incluye soporte para modo simulación.

---

## 6. Dependencias con otros módulos

Este módulo depende directamente de:

- `c_motor_trazabilidad`
  - Función: `analizar`
  - Rol: fuente principal de historial de movimientos

- `d_analizador_errores`
  - Función: `ejecutar_analisis`
  - Rol: detección de inconsistencias en trazabilidad

- `e_sugeridor_correcciones`
  - Función: `ejecutar_sugerencias`
  - Rol: generación de acciones correctivas

- `a_00_config`
  - Rol: configuración global del sistema

---

## 7. Flujo lógico general

### Flujo base de análisis

1. Se solicita un `codigo_producto`
2. Se obtiene historial desde el motor de trazabilidad
3. Se ejecuta análisis de errores
4. Se generan sugerencias
5. Se construye reporte o snapshot

---

### Flujo comparativo

1. Se genera estado inicial (antes)
2. Opcionalmente se aplican cambios externos
3. Se genera estado final (después)
4. Se comparan ambos estados
5. Se evalúa impacto (mejoró / empeoró / igual)

---

### Flujo masivo

1. Se iteran múltiples productos
2. Se ejecuta análisis individual por cada uno
3. Se clasifican según presencia de errores/sugerencias
4. Se consolidan listas globales

---

## 8. Casos críticos o riesgos

- **Dependencia fuerte de módulos externos**
  - Si falla `analizar`, todo el sistema de reportes queda inoperativo

- **Complejidad de estructuras de errores/sugerencias**
  - No hay validación estricta de esquema de datos

- **Comparaciones basadas en coincidencia simple**
  - Riesgo de falsos positivos/negativos si cambian estructuras

- **Ejecución de cambios externos**
  - `aplicar_cambios_fn` introduce riesgo de mutación del sistema en runtime

- **Uso intensivo de prints**
  - Baja escalabilidad para entornos productivos o logs estructurados

---

## 9. Interacción con el sistema de trazabilidad

Este módulo actúa como **capa superior de interpretación y control** dentro del ecosistema:

- Consume el historial generado por el motor de trazabilidad
- Interpreta errores detectados por el analizador
- Integra sugerencias del sistema de corrección
- Evalúa el impacto de cambios en el tiempo
- Permite validar el sistema antes/después de modificaciones

### Posición dentro del sistema

- `c_motor_trazabilidad` → fuente de datos
- `d_analizador_errores` → detección
- `e_sugeridor_correcciones` → optimización
- `g_reportes.py` → interpretación y validación final

---

## 10. Rol arquitectónico

Este módulo funciona como:

- **Orquestador de análisis**
- **Capa de validación de consistencia**
- **Motor de reporting operativo**
- **Herramienta de evaluación de impacto de cambios**

Es un componente clave para asegurar la confiabilidad del sistema de trazabilidad antes de aplicar correcciones en producción.









# h_validadores.py — Módulo de Validación de Trazabilidad de Stock

## Responsabilidad del módulo

Este módulo centraliza la validación de consistencia del historial de movimientos de stock reconstruido dentro del sistema de trazabilidad. Su objetivo es detectar inconsistencias, anomalías numéricas y errores de reconstrucción en los eventos que componen la evolución del stock de productos.

Funciona como una capa de control de integridad lógica sobre datos ya procesados por el motor de reconstrucción.

---

## Problema que resuelve dentro del sistema

Durante la reconstrucción del stock a partir de eventos históricos (ventas, conteos, ajustes, facturas, etc.), pueden surgir errores como:

- Descuadres entre stock previo y valor anterior reportado
- Saltos imposibles en la evolución del stock
- Valores nulos en campos críticos
- Movimientos mal formados o incompletos
- Inconsistencias entre valores originales y reconstruidos

Este módulo detecta esas fallas y las clasifica para auditoría y depuración del sistema.

---

## Entradas (inputs)

- `historial (list[dict])`
  Lista de eventos de stock reconstruido, donde cada evento puede contener:
  - stock_reconstruido
  - valor_anterior_reconstruido
  - nuevo_valor_reconstruido
  - valor_anterior
  - nuevo_valor
  - movimiento
  - cantidad
  - otros metadatos del evento

---

## Salidas (outputs)

Retorna un diccionario estructurado con:

- `total_inconsistencias (int)`
  Cantidad total de errores detectados

- `inconsistencias (list[dict])`
  Lista detallada de anomalías con:
  - índice del evento
  - tipo de inconsistencia
  - datos relevantes del evento

- `resumen (dict)`
  Conteo agregado por tipo de inconsistencia

---

## Funciones principales

### Validación de historial
- `validar_historial`
  Ejecuta todas las reglas de validación sobre la secuencia completa de eventos.

- `ejecutar_validaciones`
  API principal del módulo. Devuelve resultado estructurado listo para consumo externo.

---

### Validaciones de integridad de datos
- `validar_stock_none`
  Detecta ausencia de stock reconstruido.

- `validar_valores_none`
  Detecta valores nulos en campos de reconstrucción de valores.

---

### Validaciones de consistencia lógica
- `validar_consistencia_con_stock_previo`
  Verifica coherencia entre stock previo y valor anterior del evento, ignorando movimientos excluidos o de reseteo.

- `validar_nuevo_valor`
  Compara valores originales vs reconstruidos para detectar divergencias.

---

### Validaciones de comportamiento del stock
- `validar_salto_excesivo`
  Detecta variaciones abruptas de stock entre eventos consecutivos.

- `validar_stock_negativo`
  Identifica estados inválidos de stock por debajo de umbrales permitidos.

---

### Validaciones de integridad operativa
- `validar_movimiento_sin_cantidad`
  Detecta movimientos críticos (ventas/facturas) sin cantidad asociada.

---

### Utilidades
- `resumir_inconsistencias`
  Agrupa y contabiliza inconsistencias por tipo.

---

## Dependencias con otros módulos

- `a_00_config`
  Provee constantes de control del sistema:
  - tolerancias numéricas
  - umbrales de stock
  - tipos de movimiento a ignorar o tratar como reset

- `a_db`
  Importado pero no utilizado directamente en este módulo (posible futura expansión para logging o auditoría persistente)

- `datetime`
  Utilizado para parsing de fechas en validaciones auxiliares

---

## Flujo lógico general

1. Se recibe un historial de eventos reconstruidos.
2. Se clona la estructura para evitar efectos colaterales.
3. Se itera secuencialmente evento por evento.
4. Para cada evento:
   - Se ejecutan múltiples validaciones independientes.
   - Se compara contra el evento previo cuando corresponde.
5. Se acumulan inconsistencias detectadas.
6. Se genera un resumen agregado por tipo.
7. Se retorna un objeto estructurado para análisis.

---

## Casos críticos o riesgos

- **Dependencia fuerte de configuración externa**
  Cambios en tolerancias o listas de movimientos pueden alterar completamente el comportamiento del validador.

- **Falsos positivos por datos incompletos**
  Eventos con campos nulos pueden generar inconsistencias que no reflejan errores reales del sistema.

- **Orden del historial crítico**
  El módulo asume secuencia cronológica correcta; un orden incorrecto invalida los resultados.

- **Comparaciones numéricas sensibles**
  Uso de tolerancias puede ocultar o amplificar errores dependiendo del ajuste.

- **Importación no utilizada (`db`)**
  Sugiere posible expansión futura o deuda técnica.

---

## Interacción con el sistema de trazabilidad

Este módulo se integra como capa final de control dentro del pipeline de trazabilidad de stock:

1. Reconstrucción del stock desde eventos históricos
2. Normalización de datos de eventos
3. Validación de consistencia (este módulo)
4. Reporte o visualización de errores
5. Posible auditoría o corrección posterior

Su salida alimenta interfaces de análisis, depuración y control de calidad del sistema POS.

---

## Observación arquitectónica

Este módulo funciona como un **motor de auditoría pasivo**, no modifica datos, únicamente detecta y clasifica inconsistencias para permitir decisiones posteriores en capas superiores del sistema.









# i_simulador.py — Módulo de Simulación de Estado y Comparación de Trazabilidad


# ESTE ARCHIVO FUE ABANDONADO, no se usa.

## 1. Responsabilidad del módulo

Este módulo es el motor de simulación del sistema de trazabilidad de stock. Su función principal es generar estados completos de productos, ejecutar análisis sobre su historial, aplicar validaciones, detectar errores, generar sugerencias y comparar escenarios “antes vs después” ante cambios simulados en el sistema.

Actúa como una capa de orquestación que coordina otros módulos analíticos sin contener lógica de negocio profunda por sí mismo.

---

## 2. Problema que resuelve dentro del sistema

El sistema necesita evaluar el impacto de cambios sobre la trazabilidad de productos (por ejemplo, modificaciones de stock, correcciones o ajustes históricos) sin afectar datos reales.

Este módulo resuelve:

- Simulación de cambios sobre productos sin persistencia directa
- Evaluación comparativa de estados históricos vs futuros
- Medición del impacto de errores, inconsistencias y sugerencias
- Consolidación de métricas de calidad de trazabilidad

---

## 3. Entradas (inputs)

### A nivel producto:
- `codigo` (str): identificador del producto

### A nivel simulación:
- `funcion_aplicadora` (callable opcional): función externa que modifica el estado del sistema durante la simulación

### A nivel batch:
- `codigos` (list[str]): lista de productos a simular

---

## 4. Salidas (outputs)

### Simulación individual (`simular_producto`)
Devuelve un objeto con:

- `codigo`
- `antes`: estado completo previo a la simulación
- `despues`: estado posterior a la simulación
- `comparacion`: métricas comparativas entre ambos estados

### Simulación global (`simular_productos`)
- Diccionario de resultados por código de producto
- Puede incluir errores por producto individual

### Resumen global (`generar_resumen_global`)
- Estadísticas agregadas del conjunto simulado:
  - Total de productos
  - Productos que mejoran/empeoran/igual
  - Totales de inconsistencias, errores y sugerencias (antes y después)

---

## 5. Funciones principales

### `generar_estado_producto(codigo)`
Construye el estado completo de un producto incluyendo:
- Historial reconstruido
- Validaciones estructurales
- Análisis de errores
- Sugerencias de corrección
- Stock final calculado

---

### `simular_producto(codigo, funcion_aplicadora)`
Orquesta una simulación completa:
- Captura estado “antes”
- Ejecuta función externa de modificación (si existe)
- Captura estado “después”
- Genera comparación de impacto

---

### `comparar_estados(antes, despues)`
Compara métricas entre dos estados:
- Inconsistencias
- Errores
- Sugerencias
- Desglose por tipo de evento en cada categoría

---

### `simular_productos(codigos, funcion_aplicadora)`
Ejecuta simulación masiva con manejo de errores por producto.

---

### `generar_resumen_global(resultados)`
Agrega métricas de múltiples simulaciones:
- Totales globales
- Balance de mejora/deterioro
- Suma de inconsistencias, errores y sugerencias
- Clasificación del impacto por producto

---

### `ejecutar_simulacion(codigo, funcion_aplicadora)`
Wrapper simplificado de `simular_producto`.

---

## 6. Dependencias con otros módulos

Este módulo depende directamente de:

- `j_reconstructor`: reconstrucción del estado histórico y stock final
- `h_validadores`: detección de inconsistencias estructurales
- `d_analizador_errores`: análisis de errores del historial
- `e_sugeridor_correcciones`: generación de recomendaciones de corrección
- `copy.deepcopy`: aislamiento del historial simulado

---

## 7. Flujo lógico general

1. Reconstrucción del estado del producto
2. Copia aislada del historial
3. Ejecución de validaciones
4. Análisis de errores
5. Generación de sugerencias
6. (Opcional) Aplicación de cambios simulados
7. Reconstrucción del estado posterior
8. Comparación de métricas antes vs después
9. Agregación de resultados globales (si aplica)

---

## 8. Casos críticos o riesgos

- **Dependencia fuerte de módulos externos**: fallos en reconstrucción o validación impactan toda la simulación
- **Mutabilidad indirecta**: si la función aplicadora no está bien aislada puede afectar estado real del sistema
- **Coste computacional elevado** en simulaciones masivas
- **Inconsistencias en historial** pueden distorsionar comparaciones
- **Falta de validación de `funcion_aplicadora`** puede introducir efectos secundarios no controlados

---

## 9. Interacción con el sistema de trazabilidad

Este módulo actúa como capa de análisis superior dentro del sistema:

- Consume datos generados por la capa de reconstrucción de historial
- Interpreta resultados de validadores y analizadores
- No modifica directamente la base de datos
- Permite evaluar impacto de cambios antes de aplicarlos en producción
- Sirve como herramienta de auditoría predictiva del sistema POS

---

## 10. Rol arquitectónico

`i_simulador.py` funciona como un **motor de simulación y evaluación de impacto**, ubicado por encima de la lógica de reconstrucción y análisis.

Su valor dentro del sistema es permitir decisiones seguras antes de ejecutar cambios reales en la trazabilidad de stock.









# j_reconstructor.py — Módulo de Reconstrucción de Stock

## 1. Responsabilidad del módulo

Este módulo implementa el **motor de reconstrucción histórica de stock por producto**, a partir de eventos de movimiento registrados en el sistema.

Su función principal es recalcular el stock teórico en el tiempo, aplicando reglas específicas según el tipo de movimiento (normal, reseteo, conteo, factura, etc.), garantizando una trazabilidad coherente del estado del inventario.

---

## 2. Problema que resuelve dentro del sistema

En sistemas de stock con múltiples fuentes de actualización (ventas, facturas, conteos manuales, ajustes), el valor de stock puede volverse inconsistente o perder trazabilidad.

Este módulo resuelve:

- Reconstrucción del stock desde eventos históricos
- Corrección de inconsistencias entre `valor_anterior` y `nuevo_valor`
- Unificación de reglas de impacto según tipo de movimiento
- Generación de una línea de tiempo confiable del stock real

---

## 3. Entradas (inputs)

### Entrada principal:
- `codigo_producto` (str): identificador del producto
- `fecha_inicio` (datetime/string): punto inicial de reconstrucción
- `fecha_fin` (datetime/string | opcional): límite superior del análisis

### Dependencias de datos:
- Historial de eventos de stock (movimientos)
- Configuración de tipos de movimiento y reglas asociadas

---

## 4. Salidas (outputs)

### Salida principal (dict):
- `codigo`: producto procesado
- `total_movimientos`: cantidad de eventos procesados
- `historial`: lista de eventos enriquecidos con:
  - `stock_reconstruido`
  - `valor_anterior_reconstruido`
  - `nuevo_valor_reconstruido`
- `stock_final`: estado final del stock tras reconstrucción

### Salida alternativa:
- Resultados por lote de múltiples productos con manejo de errores individual

---

## 5. Funciones principales

### `reconstruir_producto()`
Motor central del módulo. Ejecuta la reconstrucción completa del stock de un producto aplicando reglas de negocio por tipo de movimiento.

### `reconstruir_productos()`
Orquesta la reconstrucción en batch para múltiples productos, aislando errores por código.

### `ejecutar_reconstruccion()`
API simplificada de entrada al motor de reconstrucción.

---

### Funciones auxiliares

- `norm()`: normalización de textos para comparación de movimientos
- `to_float()`: conversión segura de valores numéricos
- `round_safe()`: normalización de precisión numérica del stock
- `parse_fecha()`: conversión de fechas para ordenamiento temporal
- `es_movimiento_reseteo()`: identifica eventos que reinician o alteran base de stock
- `usar_valor_anterior_real()`: define si se debe respetar valor anterior original
- `usar_nuevo_valor_directo()`: define si el nuevo valor debe tomarse como fuente confiable
- `calcular_diferencia()`: calcula delta entre valores de evento

---

## 6. Dependencias con otros módulos

- `a_00_config`: reglas de clasificación de movimientos, prioridades y constantes globales
- `a_db`: acceso a base de datos del sistema
- `b_loader_movimientos`: extracción del historial de eventos (`obtener_eventos`)
- `e_sugeridor_correcciones`: validación de consistencia del último stock positivo (`buscar_ultimo_positivo`)

---

## 7. Flujo lógico general

1. Se obtienen eventos históricos del producto
2. Se ordenan por fecha y prioridad de tipo de movimiento
3. Se determina un stock base confiable (último valor positivo)
4. Se itera cronológicamente sobre los eventos:
   - Se clasifica el tipo de movimiento
   - Se aplica lógica de impacto (reseteo, factura, ajuste o movimiento normal)
   - Se calcula nuevo stock teórico
   - Se normaliza y registra el estado reconstruido
5. Se actualiza el stock acumulado solo cuando corresponde según reglas del tipo de evento
6. Se devuelve el historial reconstruido con stock consistente

---

## 8. Casos críticos o riesgos

### 8.1 Ambigüedad en movimientos de reseteo
Algunos eventos pueden depender de valores externos (`valor_anterior`, `nuevo_valor`), lo que puede generar reconstrucciones inconsistentes si faltan datos.

### 8.2 Dependencia del último stock positivo
El punto de partida del stock depende de heurísticas externas, lo que puede afectar toda la reconstrucción si es incorrecto.

### 8.3 Doble fuente de verdad
El sistema mezcla:
- valores históricos originales
- valores reconstruidos

Esto puede generar discrepancias si no se controla estrictamente qué fuente prevalece.

### 8.4 Ordenamiento de eventos
El orden depende de fecha + prioridad de movimiento; errores en esta jerarquía pueden alterar completamente la reconstrucción.

### 8.5 Movimientos especiales (facturas / conteos)
Algunos eventos no modifican stock directamente pero sí influyen indirectamente, lo que requiere reglas muy estrictas para evitar drift.

---

## 9. Interacción con el sistema de trazabilidad

Este módulo actúa como **motor central de reconstrucción histórica**, y se integra con:

- **Loader de movimientos (`b_loader_movimientos`)**  
  Fuente primaria de eventos históricos.

- **Motor de correcciones (`e_sugeridor_correcciones`)**  
  Define punto de arranque confiable del stock.

- **Configuración global (`a_00_config`)**  
  Define reglas de clasificación de movimientos y comportamiento del sistema.

- **Base de datos (`a_db`)**  
  Soporte estructural para persistencia y consultas.

---

## Rol dentro de la arquitectura

`j_reconstructor.py` es el componente que transforma el sistema de stock desde un modelo **transaccional** hacia un modelo **reconstruible y auditable**, permitiendo:

- Auditoría histórica completa
- Corrección de inconsistencias retroactivas
- Simulación de estados de inventario en el tiempo
- Base para análisis avanzado de trazabilidad









# k_corrige_errores_iniciales.py

## Responsabilidad del módulo

Este módulo se encarga de ejecutar un proceso automático de corrección de inconsistencias detectadas en la trazabilidad de stock. Su objetivo es auditar, ajustar y reparar desfasajes entre el historial de movimientos y la reconstrucción real del stock, generando correcciones persistentes en la base de datos.

Actúa como una capa de “auto-reparación” del sistema de trazabilidad, aplicando ajustes tanto correctivos como compensatorios sobre eventos históricos.

---

## Problema que resuelve dentro del sistema

El sistema de trazabilidad puede generar inconsistencias debido a:

- Desorden temporal en movimientos (especialmente conteos y ajustes históricos)
- Movimientos mal registrados o faltantes
- Diferencias entre stock reconstruido vs valores almacenados
- Inconsistencias no detectadas por el analizador principal
- Errores heredados de cargas históricas de datos

Este módulo corrige esas inconsistencias generando ajustes automáticos o actualizando registros existentes.

---

## Entradas (inputs)

- `codigo` del producto a analizar
- Historial de movimientos obtenido desde base de datos
- Reconstrucción de stock calculada por el motor de trazabilidad
- Inconsistencias detectadas por el analizador (`ejecutar_analisis`)
- Datos de productos (descripción)
- Registros históricos en `historial_de_articulos`

---

## Salidas (outputs)

- Actualizaciones en base de datos:
  - Correcciones de registros existentes
  - Inserción de ajustes inventados de auditoría
- Logs en consola del proceso de corrección
- Revalidación final de inconsistencias
- Estado final de consistencia del producto

---

## Funciones principales

### `corregir_errores_iniciales(codigo)`
Orquesta todo el proceso de detección, generación y aplicación de correcciones sobre un producto específico.

### `generar_correcciones(codigo, historial, inconsistencias)`
Construye un set de correcciones basadas en diferencias entre reconstrucción de stock y eventos inconsistentes.

### `normalizar_tiempo_conteos(historial)`
Corrige desorden temporal entre eventos de conteo para evitar errores en la reconstrucción del stock.

### `insertar_ajuste(codigo, descripcion, valor_anterior, nuevo_valor, fecha)`
Inserta un ajuste artificial en el historial como mecanismo de reparación de trazabilidad.

### `obtener_descripcion(codigo)`
Recupera la descripción del producto desde la tabla de productos.

### `parse_fecha(x)`
Normaliza múltiples formatos de fecha a objetos datetime.

### `fecha_media(f1, f2)`
Calcula un punto temporal intermedio entre dos eventos consecutivos.

---

## Dependencias con otros módulos

- `a_00_config`: configuración general del sistema
- `a_db`: acceso a base de datos y ejecución de queries
- `b_loader_movimientos`: obtención de eventos históricos del producto
- `c_motor_trazabilidad`: reconstrucción del stock a partir del historial
- `d_analizador_errores`: detección de inconsistencias en la trazabilidad

---

## Flujo lógico general

1. Se solicita un código de producto
2. Se cargan movimientos históricos desde la base de datos
3. Se normaliza el orden temporal de eventos críticos
4. Se reconstruye el stock completo del producto
5. Se detectan inconsistencias mediante el analizador
6. Se generan correcciones basadas en diferencias estructurales
7. Se aplican correcciones:
   - Updates directos para casos especiales (ej. cargas de facturas)
   - Inserts de ajustes artificiales para el resto de casos
8. Se guarda la transacción en base de datos
9. Se ejecuta una nueva validación de consistencia

---

## Casos críticos o riesgos

- **Modificación de historial real:** el módulo altera datos históricos, lo que puede afectar auditorías si no está controlado.
- **Ajustes artificiales:** inserta registros que no provienen de eventos reales.
- **Dependencia fuerte del orden temporal:** errores en fechas pueden generar correcciones incorrectas.
- **Posible sobrecorrección:** puede introducir nuevos ajustes en cascada si el analizador no converge.
- **Actualizaciones SQL sensibles:** updates condicionados por fecha pueden afectar múltiples registros si no son únicos.
- **Inconsistencias no detectadas por duplicidad de índices:** riesgo de doble corrección si no se deduplica correctamente.

---

## Interacción con el sistema de trazabilidad

Este módulo actúa como una capa superior al motor de trazabilidad:

- Consume el historial bruto desde el loader
- Usa el motor de reconstrucción como referencia de verdad operativa
- Se apoya en el analizador de inconsistencias para decidir qué corregir
- Escribe directamente en la tabla `historial_de_articulos`, alterando la historia del sistema
- Revalida el sistema después de aplicar cambios para asegurar convergencia

En el ecosistema general, funciona como un **corrector automático post-análisis**, cerrando el ciclo:

**Carga → Reconstrucción → Análisis → Corrección → Revalidación**









# z_test_trazabilidad.py — Módulo Orquestador de Trazabilidad

## Responsabilidad del módulo

Este módulo actúa como **punto de entrada y orquestador principal del sistema de trazabilidad de stock**. Su función es coordinar el flujo completo de análisis, detección de inconsistencias, sugerencias de corrección, aplicación de cambios y ejecución de procesos de auditoría automática sobre productos.

No implementa lógica de negocio profunda, sino que **integra y ejecuta los distintos módulos especializados del sistema**.

---

## Problema que resuelve dentro del sistema

Centraliza el proceso de trazabilidad de productos que involucra:

- Reconstrucción del historial de stock por producto
- Detección de inconsistencias en movimientos
- Generación de sugerencias correctivas
- Aplicación controlada de correcciones
- Activación de mecanismos de fallback (auditoría externa)

Evita la dispersión de lógica entre módulos y permite ejecutar un flujo completo de validación y corrección de datos de stock.

---

## Entradas (inputs)

- Código de producto (`codigo`)
- Base de datos interna (`base_de_datos_interna.db`)
- Historial de movimientos del producto (obtenido desde motor de trazabilidad)
- Estado actual de scripts auxiliares (Excel y auditoría)

---

## Salidas (outputs)

- Historial reconstruido de stock por producto
- Reportes de inconsistencias detectadas
- Sugerencias de corrección
- Cambios aplicados al sistema (si se confirma)
- Ejecución de scripts externos de auditoría (Excel + diagnóstico)
- Logs por consola del estado del proceso

---

## Funciones principales

### `obtener_datos(codigo)`
Obtiene el resultado completo del motor de trazabilidad y extrae el historial de movimientos del producto.

### `ver_historial(codigo)`
Muestra el historial reconstruido de stock de un producto de forma cronológica.

### `ver_errores(codigo)`
Ejecuta el análisis de inconsistencias sobre el historial del producto y muestra los errores detectados.

### `ver_sugerencias(codigo)`
Genera sugerencias de corrección basadas en el historial de movimientos del producto.

### `ver_reporte(codigo)`
Genera un reporte simple del estado de trazabilidad del producto.

### `proceso_automatico_trazabilidad()`
Orquesta el proceso completo de auditoría masiva de productos:
- Itera sobre todos los códigos de producto
- Ejecuta análisis de inconsistencias
- Aplica correcciones automáticas iterativas
- Ejecuta fallback de auditoría externa si el error persiste

### `aplicar(codigo)`
Aplica sugerencias de corrección al sistema luego de confirmación del usuario.

### `menu()`
Interfaz de consola para ejecutar manualmente los distintos procesos de trazabilidad.

---

## Dependencias con otros módulos

Este módulo depende directamente de:

- `a_db`: conexión a base de datos
- `c_motor_trazabilidad`: reconstrucción de historial de stock
- `d_analizador_errores`: detección de inconsistencias
- `e_sugeridor_correcciones`: generación de sugerencias
- `f_aplicador_cambios`: aplicación de correcciones
- `g_reportes`: generación de reportes
- `k_corrige_errores_iniciales`: corrección automática inicial
- Scripts externos de Excel y diagnóstico

También utiliza librerías estándar:
- `subprocess`
- `shutil`
- `re`
- `os`, `sys`

---

## Flujo lógico general

1. Usuario ingresa o selecciona código de producto
2. Se reconstruye el historial de movimientos del producto
3. Se ejecuta análisis de inconsistencias
4. Si no hay errores → se finaliza el proceso
5. Si hay errores:
   - Se intentan hasta 3 ciclos de corrección automática
   - Se reanaliza el estado en cada ciclo
6. Si persisten errores:
   - Se activa modo auditoría avanzada
   - Se copia base de datos
   - Se modifica y ejecuta script Excel
   - Se ejecuta diagnóstico externo
7. El sistema finaliza o continúa con el siguiente código

---

## Casos críticos o riesgos

- **Modificación automática de scripts externos (Excel)**  
  Riesgo de corrupción o alteración no deseada del flujo de exportación.

- **Sobrescritura de base de datos**  
  El backup manual vía copia puede no ser suficiente en escenarios de fallo.

- **Ejecución de subprocessos externos**  
  Dependencia fuerte del entorno del sistema operativo.

- **Corrección automática iterativa**  
  Riesgo de bucles lógicos si el motor de corrección no converge.

- **Falta de control transaccional**  
  Las correcciones no parecen estar encapsuladas en transacciones seguras.

---

## Interacción con el resto del sistema de trazabilidad

Este módulo funciona como **capa superior de coordinación del sistema completo**:

- Consume el motor de reconstrucción de stock
- Interpreta análisis de errores como criterio de decisión
- Activa el generador de sugerencias como sistema de soporte
- Puede aplicar cambios directamente al sistema productivo
- Dispara procesos externos de auditoría cuando la lógica interna no es suficiente

En términos arquitectónicos, actúa como un **orquestador híbrido entre motor de trazabilidad, sistema de reglas y capa de auditoría externa**.