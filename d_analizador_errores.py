# d_analizador_errores.py
from copy import deepcopy
from a_00_config import *

# =========================================================
# UTILIDAD
# =========================================================

def es_valido_numero(x):

    try:

        if x is None or x == "":
            return False

        float(x)

        return True

    except:
        return False


def norm(x):

    return x.strip().lower() if isinstance(x, str) else x


def normalizar(x):

    try:
        return float(x)

    except:
        return None


def coincide_con_tolerancia(a, b):

    if a is None or b is None:
        return False

    if abs(a - b) < TOLERANCIA_NUMERICA:
        return True

    if round(a, 2) == round(b, 2):
        return True

    return False


# =========================================================
# ANALIZADOR PRINCIPAL
# =========================================================

def analizar_errores(historial):

    errores = []

    if not historial:
        return errores

    data = deepcopy(historial)

    for i in range(len(data)):
        actual = data[i]

        mov = norm(actual.get("movimiento"))

        stock_actual = actual.get("stock_reconstruido")

        valor_anterior = actual.get("valor_anterior")

        sa = normalizar(stock_actual)

        va = normalizar(valor_anterior)

        # =================================================
        # IGNORAR MOVIMIENTOS
        # =================================================

        if mov in MOVIMIENTOS_IGNORE:
            continue

        # =================================================
        # STOCK NONE
        # =================================================

        if stock_actual is None:

            errores.append({
                "indice": i,
                "tipo": "stock_none",
                "detalle": actual
            })

            continue

        # =================================================
        # SALTOS EXCESIVOS
        # =================================================

        if i > 0:

            prev = data[i - 1].get("stock_reconstruido")

            prev_n = normalizar(prev)

            if (
                prev_n is not None
                and sa is not None
                and abs(sa - prev_n) > SALTO_MAXIMO_PERMITIDO
            ):

                errores.append({
                    "indice": i,
                    "tipo": "salto_excesivo_stock",
                    "anterior": prev_n,
                    "actual": sa,
                    "diferencia": sa - prev_n,
                    "detalle": actual
                })

        # =================================================
        # VALIDACIÓN DE CONSISTENCIA HISTÓRICA
        # =================================================

        # valor_anterior inválido
        if va is None:
            continue

        # =================================================
        # REFERENCIAS ESPERADAS
        # =================================================

        te1 = None
        te2 = None

        # movimientos visuales:
        # deben coincidir SOLO con el stock inmediatamente anterior
        if mov in [
            "carga de facturas (historial)",
            "conteo de stock (historial)"
        ]:
            ultimos = []
            for k in range(i - 1, -1, -1):
                val = normalizar(data[k].get("stock_reconstruido"))
                if val is not None:
                    ultimos.append(val)
                if len(ultimos) == 2:
                    break
            te1 = ultimos[0] if len(ultimos) >= 1 else None
            te2 = ultimos[1] if len(ultimos) >= 2 else None

        # resto de movimientos:
        # tolerar últimas 2 referencias
        else:

            ultimos = []

            for k in range(i - 1, -1, -1):

                val = data[k].get("stock_reconstruido")

                val = normalizar(val)

                if val is not None:
                    ultimos.append(val)

                if len(ultimos) == 2:
                    break

            te1 = ultimos[0] if len(ultimos) >= 1 else None
            te2 = ultimos[1] if len(ultimos) >= 2 else None

        # no hay referencia
        if te1 is None and te2 is None:
            continue

        coincide = False

        if coincide_con_tolerancia(va, te1):
            coincide = True

        if coincide_con_tolerancia(va, te2):
            coincide = True


        if not coincide:

            # =====================================================
            # FILTROS DE FALSOS POSITIVOS
            # =====================================================

            if mov == "conteo de stock (historial)":

                # PATRÓN 1: corrección de empleado
                for k in range(i - 1, -1, -1):
                    mov_k = norm(data[k].get("movimiento"))
                    if mov_k == "conteo de stock (historial)":
                        nv_k = normalizar(data[k].get("nuevo_valor"))
                        if coincide_con_tolerancia(va, nv_k):
                            coincide = True
                        break
                    if mov_k not in ["conteo de stock"]:
                        break

                # PATRÓN 2: conteo invertido o reafirmación
                if not coincide:
                    nv = normalizar(actual.get("nuevo_valor"))
                    if coincide_con_tolerancia(nv, sa) and coincide_con_tolerancia(va, te1):
                        coincide = True
                    elif coincide_con_tolerancia(va, nv) and (
                        coincide_con_tolerancia(va, te1) or
                        (coincide_con_tolerancia(va, te2) and coincide_con_tolerancia(te1, te2))
                    ):
                        coincide = True
                        coincide = True
            # PATRÓN 3: bloque de factura desordenado
            if mov == "carga de facturas (historial)":
                nv = normalizar(actual.get("nuevo_valor"))
                if coincide_con_tolerancia(nv, sa) and coincide_con_tolerancia(va, te1):
                    coincide = True

            # =====================================================
            if not coincide:

                diferencia_1 = None
                diferencia_2 = None

                if te1 is not None:
                    diferencia_1 = va - te1

                if te2 is not None:
                    diferencia_2 = va - te2

                errores.append({
                    "indice": i,
                    "tipo": "inconsistencia_historica",
                    "valor_anterior": va,
                    "stock_esperado_1": te1,
                    "stock_esperado_2": te2,
                    "diferencia_1": diferencia_1,
                    "diferencia_2": diferencia_2,
                    "detalle": actual
                })


        # =================================================
        # MOVIMIENTOS SIN CANTIDAD
        # =================================================

        if mov in [
            "ventas detalladas",
            "facturas detalladas"
        ]:

            cant = actual.get("cantidad")

            if (
                cant is None
                or not es_valido_numero(cant)
            ):

                errores.append({
                    "indice": i,
                    "tipo": "movimiento_sin_cantidad",
                    "detalle": actual
                })

    return errores


# =========================================================
# RESUMEN
# =========================================================

def resumir_errores(errores):

    resumen = {}

    for e in errores:

        tipo = e.get("tipo", "desconocido")

        if tipo not in resumen:

            resumen[tipo] = 0

        resumen[tipo] += 1

    return resumen


# =========================================================
# API SIMPLE DEL MÓDULO
# =========================================================

def ejecutar_analisis(historial):

    errores = analizar_errores(historial)

    resumen = resumir_errores(errores)

    inconsistencias = [
        e for e in errores
        if e["tipo"] == "inconsistencia_historica"
    ]

    return {

        # lista completa
        "errores": errores,

        # totales
        "total_errores": len(errores),

        # inconsistencias reales
        "inconsistencias": inconsistencias,

        "total_inconsistencias": len(inconsistencias),

        # resumen agrupado
        "resumen": resumen
    }
