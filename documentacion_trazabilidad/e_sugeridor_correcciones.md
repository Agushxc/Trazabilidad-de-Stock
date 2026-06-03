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