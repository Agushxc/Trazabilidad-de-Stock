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