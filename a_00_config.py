#a_00_config.py

# CONFIGURACIÓN GENERAL
DB_FILE = "base_de_datos_interna.db"
FECHA_INICIO_DEFAULT = "2025-07-15 00:00:00"

# REGLAS DE TRAZABILIDAD
UMBRAL_NEGATIVO = -0.01
TOLERANCIA_CERO = 0.001
TOLERANCIA_NUMERICA = 0.01
UMBRAL_RUIDO = 0.1
SALTO_MAXIMO_PERMITIDO = 100000

# FACTURAS Y MOVIMIENTOS
DIAS_TOLERANCIA_FACTURA = 7

MOVIMIENTOS_SUMA = {
    "facturas detalladas",
}

MOVIMIENTOS_RESTA = {
    "ventas detalladas",
}

MOVIMIENTOS_RESETEO = [
    "a.b.m. (historial)",
    "ajuste manual con auditoría inventada (historial)",
    "control de inventario (historial)",
    "corrección manual antes de cargar factura (historial)",
    "pedidos, control de inventario, administrar (historial)"
]

MOVIMIENTOS_RESETEO_VALOR_ANTERIOR = [
    "a.b.m. (historial)",
    "ajuste manual con auditoría inventada (historial)",
    "carga de facturas (historial)",
    "conteo de stock (historial)",
    "control de inventario (historial)",
    "pedidos, control de inventario, administrar (historial)"
]

MOVIMIENTOS_RESETEO_NUEVO_VALOR = [
    "corrección manual antes de cargar factura (historial)"
]

MOVIMIENTOS_CONTEO_DIRECTO = [
    "conteo de stock"
]

MOVIMIENTOS_IGNORE = [
    "modificar fila en cargar factura (historial)"
]

PRIORIDAD_MOVIMIENTO = {
    "historial": 0,
    "conteo": 1,
    "compra": 2,
    "venta": 3
}

# MODOS DEL SISTEMA
MODO_DEBUG = False
APLICAR_CORRECCIONES_AUTOMATICO = False
GENERAR_EXCEL = True