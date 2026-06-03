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