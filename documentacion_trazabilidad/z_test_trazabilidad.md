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