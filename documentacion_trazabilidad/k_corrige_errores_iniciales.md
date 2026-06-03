# k_corrige_errores_iniciales.py

## Responsabilidad del módulo

Este módulo se encarga de ejecutar un proceso automático de corrección de inconsistencias detectadas en la trazabilidad de stock. Su objetivo es auditar, ajustar y reparar desfasajes entre el historial de movimientos y la reconstrucción real del stock, generando correcciones persistentes en la base de datos.

Actúa como una capa de “auto-reparación” del sistema de trazabilidad, aplicando ajustes tanto correctivos como compensatorios sobre eventos históricos.

---

## Problema que resuelve dentro del sistema

El sistema de trazabilidad puede generar inconsistencias debido a:

- Desorden temporal en movimientos (especialmente conteos y ajustes históricos)
- Movimientos mal registrados o faltantes
- Diferencias entre stock reconstruido vs valores almacenados
- Inconsistencias no detectadas por el analizador principal
- Errores heredados de cargas históricas de datos

Este módulo corrige esas inconsistencias generando ajustes automáticos o actualizando registros existentes.

---

## Entradas (inputs)

- `codigo` del producto a analizar
- Historial de movimientos obtenido desde base de datos
- Reconstrucción de stock calculada por el motor de trazabilidad
- Inconsistencias detectadas por el analizador (`ejecutar_analisis`)
- Datos de productos (descripción)
- Registros históricos en `historial_de_articulos`

---

## Salidas (outputs)

- Actualizaciones en base de datos:
  - Correcciones de registros existentes
  - Inserción de ajustes inventados de auditoría
- Logs en consola del proceso de corrección
- Revalidación final de inconsistencias
- Estado final de consistencia del producto

---

## Funciones principales

### `corregir_errores_iniciales(codigo)`
Orquesta todo el proceso de detección, generación y aplicación de correcciones sobre un producto específico.

### `generar_correcciones(codigo, historial, inconsistencias)`
Construye un set de correcciones basadas en diferencias entre reconstrucción de stock y eventos inconsistentes.

### `normalizar_tiempo_conteos(historial)`
Corrige desorden temporal entre eventos de conteo para evitar errores en la reconstrucción del stock.

### `insertar_ajuste(codigo, descripcion, valor_anterior, nuevo_valor, fecha)`
Inserta un ajuste artificial en el historial como mecanismo de reparación de trazabilidad.

### `obtener_descripcion(codigo)`
Recupera la descripción del producto desde la tabla de productos.

### `parse_fecha(x)`
Normaliza múltiples formatos de fecha a objetos datetime.

### `fecha_media(f1, f2)`
Calcula un punto temporal intermedio entre dos eventos consecutivos.

---

## Dependencias con otros módulos

- `a_00_config`: configuración general del sistema
- `a_db`: acceso a base de datos y ejecución de queries
- `b_loader_movimientos`: obtención de eventos históricos del producto
- `c_motor_trazabilidad`: reconstrucción del stock a partir del historial
- `d_analizador_errores`: detección de inconsistencias en la trazabilidad

---

## Flujo lógico general

1. Se solicita un código de producto
2. Se cargan movimientos históricos desde la base de datos
3. Se normaliza el orden temporal de eventos críticos
4. Se reconstruye el stock completo del producto
5. Se detectan inconsistencias mediante el analizador
6. Se generan correcciones basadas en diferencias estructurales
7. Se aplican correcciones:
   - Updates directos para casos especiales (ej. cargas de facturas)
   - Inserts de ajustes artificiales para el resto de casos
8. Se guarda la transacción en base de datos
9. Se ejecuta una nueva validación de consistencia

---

## Casos críticos o riesgos

- **Modificación de historial real:** el módulo altera datos históricos, lo que puede afectar auditorías si no está controlado.
- **Ajustes artificiales:** inserta registros que no provienen de eventos reales.
- **Dependencia fuerte del orden temporal:** errores en fechas pueden generar correcciones incorrectas.
- **Posible sobrecorrección:** puede introducir nuevos ajustes en cascada si el analizador no converge.
- **Actualizaciones SQL sensibles:** updates condicionados por fecha pueden afectar múltiples registros si no son únicos.
- **Inconsistencias no detectadas por duplicidad de índices:** riesgo de doble corrección si no se deduplica correctamente.

---

## Interacción con el sistema de trazabilidad

Este módulo actúa como una capa superior al motor de trazabilidad:

- Consume el historial bruto desde el loader
- Usa el motor de reconstrucción como referencia de verdad operativa
- Se apoya en el analizador de inconsistencias para decidir qué corregir
- Escribe directamente en la tabla `historial_de_articulos`, alterando la historia del sistema
- Revalida el sistema después de aplicar cambios para asegurar convergencia

En el ecosistema general, funciona como un **corrector automático post-análisis**, cerrando el ciclo:

**Carga → Reconstrucción → Análisis → Corrección → Revalidación**