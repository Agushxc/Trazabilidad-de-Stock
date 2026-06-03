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