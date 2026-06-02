README.md
Sistema de Trazabilidad de Stock

Sistema diseñado para reconstruir, auditar, validar y corregir la evolución histórica del stock de productos a partir de múltiples fuentes de datos del POS.

El objetivo es detectar inconsistencias, reconstruir estados reales de inventario y proponer o aplicar correcciones sobre la trazabilidad histórica.

Arquitectura General
Base de Datos
       │
       ▼
b_loader_movimientos
       │
       ▼
c_motor_trazabilidad
       │
       ├─────────────► d_analizador_errores
       │
       ├─────────────► h_validadores
       │
       └─────────────► e_sugeridor_correcciones
                             │
                             ▼
                    f_aplicador_cambios
                             │
                             ▼
               k_corrige_errores_iniciales
                             │
                             ▼
                       g_reportes
                             │
                             ▼
                  z_test_trazabilidad
Componentes Principales
Módulo	Función
a_00_config.py	Configuración global y reglas de negocio
a_db.py	Acceso centralizado a SQLite
b_loader_movimientos.py	Unificación de eventos de stock
c_motor_trazabilidad.py	Reconstrucción histórica del stock
d_analizador_errores.py	Detección de inconsistencias
e_sugeridor_correcciones.py	Generación de hipótesis de corrección
f_aplicador_cambios.py	Aplicación de cambios sobre historial
g_reportes.py	Reportes y comparación de estados
h_validadores.py	Validaciones de consistencia
j_reconstructor.py	Reconstrucción avanzada del historial
k_corrige_errores_iniciales.py	Corrección automática de inconsistencias
z_test_trazabilidad.py	Orquestador principal del sistema
Flujo de Trabajo
1. Carga de movimientos

Se obtienen eventos desde:

Ventas
Facturas
Conteos
Ajustes
Historial de artículos

y se normalizan en una única línea temporal.

2. Reconstrucción

El motor calcula el stock histórico aplicando reglas de negocio para cada tipo de movimiento.

3. Validación

Se detectan:

Saltos anómalos
Stocks negativos
Valores inconsistentes
Errores de reconstrucción
4. Generación de sugerencias

Se analizan inconsistencias y se generan posibles acciones correctivas.

5. Aplicación de correcciones

Las correcciones pueden:

Reubicar facturas
Ajustar historial
Insertar eventos compensatorios
6. Revalidación

El sistema vuelve a reconstruir y analizar el historial para verificar que las inconsistencias hayan sido resueltas.

Dependencias Críticas
SQLite
Base de datos base_de_datos_interna.db
Historial de movimientos consistente
Orden cronológico correcto de eventos
Riesgos Principales
Modificación de historial real de stock.
Dependencia fuerte de la clasificación de movimientos.
Errores de fechas que alteran toda la reconstrucción.
Correcciones automáticas que pueden generar efectos en cascada.
Cambios en configuración que impactan todo el sistema.
Módulos Obsoletos
Módulo	Estado
i_simulador.py	Abandonado / no utilizado
Objetivo del Proyecto

Convertir registros históricos dispersos de stock en una línea temporal reconstruible, auditable y corregible, permitiendo detectar errores, explicar desvíos de inventario y mantener la coherencia histórica del sistema POS.