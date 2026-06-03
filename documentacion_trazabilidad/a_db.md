# Módulo: a_db.py — Capa de Acceso a Base de Datos

## Responsabilidad del módulo
Este módulo implementa una capa básica de acceso y control de la base de datos SQLite del sistema. Su responsabilidad es centralizar la conexión, ejecución de consultas y commits, proporcionando una interfaz mínima reutilizable para el resto del sistema.

Actúa como punto único de interacción con la base de datos interna, evitando que otros módulos gestionen conexiones directamente.

---

## Problema que resuelve dentro del sistema
Resuelve la necesidad de:

- Evitar conexiones dispersas a SQLite en múltiples módulos
- Centralizar la ejecución de queries SQL
- Simplificar el acceso a datos mediante una instancia global reutilizable
- Reducir duplicación de código relacionado con conexión y cursor
- Facilitar el mantenimiento del acceso a datos en todo el sistema POS

---

## Entradas (inputs)
- Sentencias SQL en formato string
- Parámetros opcionales en forma de tuplas (`params`)
- Llamadas a métodos de control de conexión (`conectar`, `commit`, `cerrar`)

---

## Salidas (outputs)
- Resultados de consultas SQL:
  - Listas de filas (`fetchall`)
  - Una sola fila (`fetchone`)
- Estado persistido en la base de datos tras `commit()`
- Conexión activa a SQLite (`sqlite3.Connection`)
- Cursor activo (`sqlite3.Cursor`)

---

## Funciones principales

### `conectar()`
Establece la conexión con la base de datos si aún no existe. Inicializa cursor y configura el formato de retorno de filas.

### `ejecutar(query, params)`
Ejecuta una consulta SQL y devuelve múltiples resultados. No realiza commit automático.

### `ejecutar_uno(query, params)`
Ejecuta una consulta SQL y devuelve un único registro.

### `commit()`
Confirma transacciones pendientes en la base de datos.

### `cerrar()`
Cierra la conexión activa y libera recursos del cursor.

---

## Dependencias con otros módulos
- `sqlite3` (librería estándar)
- `a_00_config` (importado aunque no se utiliza directamente en este módulo)
- Módulos del sistema POS que consumen `db` como instancia global

---

## Flujo lógico general
1. Un módulo del sistema solicita acceso a datos mediante `db.ejecutar()` o `db.ejecutar_uno()`
2. Si no existe conexión activa, se crea automáticamente
3. Se ejecuta la consulta SQL con parámetros opcionales
4. Se devuelven los resultados sin persistir cambios
5. Si hubo modificaciones, el módulo consumidor ejecuta `db.commit()`
6. La conexión puede mantenerse abierta durante toda la sesión o cerrarse explícitamente

---

## Casos críticos o riesgos
- **Persistencia de conexión global**: el uso de una instancia global puede generar estados compartidos no controlados en sistemas concurrentes
- **Falta de manejo de errores**: no hay captura de excepciones SQL, lo que puede interrumpir el flujo del sistema
- **Commit manual obligatorio**: riesgo de olvidos que provoquen pérdida de cambios
- **Reutilización de cursor global**: puede generar comportamientos inesperados si múltiples módulos ejecutan consultas simultáneamente
- **Dependencia implícita de estado interno** (`conn` y `cursor`)

---

## Interacción con el sistema de trazabilidad de stock
Este módulo actúa como base de persistencia para todo el sistema de trazabilidad.

Es utilizado indirectamente por:

- Módulos de stock (movimientos, ajustes, reconstrucción)
- Módulos de ventas y compras
- Módulos de reportes históricos
- Módulos de auditoría y seguimiento

En el sistema de trazabilidad, su rol es crítico porque:

- Garantiza el acceso consistente a los eventos de stock almacenados
- Permite reconstrucción histórica mediante consultas SQL
- Soporta la integridad de datos que alimentan el simulador y el reconstructor
- Funciona como capa inferior de toda la cadena de eventos del sistema

---

## Observación arquitectónica
Este módulo cumple una función de “mini ORM manual”, aunque sin abstracciones avanzadas. Es funcional y liviano, pero en sistemas de mayor escala podría evolucionar hacia:

- Context managers (`with`)
- Manejo de transacciones explícitas
- Capa de repositorios por entidad
- Control de concurrencia más robusto