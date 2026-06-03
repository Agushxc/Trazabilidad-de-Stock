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
