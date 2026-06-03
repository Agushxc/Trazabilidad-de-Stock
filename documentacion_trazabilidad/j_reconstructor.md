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