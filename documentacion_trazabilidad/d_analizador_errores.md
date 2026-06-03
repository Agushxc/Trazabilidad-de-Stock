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