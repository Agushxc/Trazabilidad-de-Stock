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