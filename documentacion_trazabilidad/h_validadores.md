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