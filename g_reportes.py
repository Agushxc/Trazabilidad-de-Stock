# g_reportes.py
from copy import deepcopy
from pprint import pprint

from c_motor_trazabilidad import analizar
from d_analizador_errores import ejecutar_analisis
from e_sugeridor_correcciones import ejecutar_sugerencias
from a_00_config import *

# UTILIDAD
def norm(x):
    return x.strip().lower() if isinstance(x, str) else x

def resumen_errores(errores):

    resumen = {}

    for e in errores:

        tipo = e.get("tipo", "desconocido")

        fecha = None

        detalle = e.get("detalle")

        if isinstance(detalle, dict):
            fecha = detalle.get("fecha")

        if tipo not in resumen:

            resumen[tipo] = {
                "cantidad": 0,
                "primera_fecha": fecha
            }

        resumen[tipo]["cantidad"] += 1

    return resumen

def imprimir_resumen_errores(resumen):

    if not resumen:
        print("Sin errores")
        return

    for tipo, data in sorted(resumen.items()):

        cantidad = data["cantidad"]

        fecha = data["primera_fecha"]

        if cantidad == 1:
            print(f"{tipo}: {cantidad} ({fecha})")
        else:
            print(
                f"{tipo}: {cantidad} "
                f"(el primero: {fecha})"
            )

# REPORTE SIMPLE
def reporte_simple(codigo_producto):

    resultado = analizar(codigo_producto)

    historial = resultado["historial"]

    analisis = ejecutar_analisis(historial)

    sugerencias = ejecutar_sugerencias(historial)

    print("\n================================================")
    print("CÓDIGO:", codigo_producto)
    print("================================================")

    print("\n-----------------------------")
    print("RESUMEN")
    print("-----------------------------")

    print("Total movimientos:", len(historial))

    # FECHA PRIMER ERROR
    primer_error_fecha = None

    if analisis["errores"]:

        detalle = analisis["errores"][0].get("detalle")

        if isinstance(detalle, dict):
            primer_error_fecha = detalle.get("fecha")

    # FECHA PRIMER SUGERENCIA
    primer_sugerencia_fecha = None

    if sugerencias["sugerencias"]:

        primer_sugerencia_fecha = (
            sugerencias["sugerencias"][0]
            .get("fecha_inicio_negativo")
        )

    # IMPRIMIR ERRORES
    if analisis["total_errores"] == 1:
        print(
            f"Total errores: "
            f"{analisis['total_errores']} "
            f"({primer_error_fecha})"
        )
    else:
        print(
            f"Total errores: "
            f"{analisis['total_errores']} "
            f"(el primero: {primer_error_fecha})"
        )

    # IMPRIMIR SUGERENCIAS
    if sugerencias["total_sugerencias"] == 1:
        print(
            f"Total sugerencias: "
            f"{sugerencias['total_sugerencias']} "
            f"({primer_sugerencia_fecha})"
        )
    else:
        print(
            f"Total sugerencias: "
            f"{sugerencias['total_sugerencias']} "
            f"(el primero: {primer_sugerencia_fecha})"
        )

    print("\n-----------------------------")
    print("TIPOS DE ERRORES")
    print("-----------------------------")

    imprimir_resumen_errores(
        resumen_errores(analisis["errores"])
    )

    print("\n-----------------------------")
    print("SUGERENCIAS")
    print("-----------------------------")

    pprint(sugerencias["sugerencias"])

    return {
        "historial": historial,
        "errores": analisis["errores"],
        "sugerencias": sugerencias["sugerencias"]
    }

# COMPARAR ERRORES
# ANTES VS DESPUÉS DE CAMBIOS
def comparar_errores(
    errores_antes,
    errores_despues
):

    antes = deepcopy(errores_antes)
    despues = deepcopy(errores_despues)

    cantidad_antes = len(antes)
    cantidad_despues = len(despues)

    diferencia = cantidad_despues - cantidad_antes

    tipos_antes = resumen_errores(antes)
    tipos_despues = resumen_errores(despues)

    nuevos_errores = []

    for e in despues:

        encontrado = False

        for a in antes:

            if (
                e.get("tipo") == a.get("tipo")
                and e.get("indice") == a.get("indice")
            ):
                encontrado = True
                break

        if not encontrado:
            nuevos_errores.append(e)

    errores_resueltos = []

    for a in antes:

        encontrado = False

        for e in despues:

            if (
                e.get("tipo") == a.get("tipo")
                and e.get("indice") == a.get("indice")
            ):
                encontrado = True
                break

        if not encontrado:
            errores_resueltos.append(a)

    return {

        # cantidades
        "cantidad_antes": cantidad_antes,
        "cantidad_despues": cantidad_despues,
        "diferencia": diferencia,

        # resúmenes
        "tipos_antes": tipos_antes,
        "tipos_despues": tipos_despues,

        # detalles
        "nuevos_errores": nuevos_errores,
        "errores_resueltos": errores_resueltos,

        # flags útiles
        "empeoro": cantidad_despues > cantidad_antes,
        "mejoro": cantidad_despues < cantidad_antes,
        "igual": cantidad_despues == cantidad_antes
    }

# IMPRIMIR COMPARACIÓN
def imprimir_comparacion(resultado):

    print("\n================================================")
    print("COMPARACIÓN DE ERRORES")
    print("================================================")

    print("\n-----------------------------")
    print("CANTIDADES")
    print("-----------------------------")

    # FECHAS ANTES
    fecha_antes = None

    tipos_antes = resultado["tipos_antes"]

    if tipos_antes:
        primer_tipo = next(iter(tipos_antes.values()))
        fecha_antes = primer_tipo.get("primera_fecha")

    # FECHAS DESPUÉS
    fecha_despues = None

    tipos_despues = resultado["tipos_despues"]

    if tipos_despues:
        primer_tipo = next(iter(tipos_despues.values()))
        fecha_despues = primer_tipo.get("primera_fecha")

    # ERRORES ANTES
    if resultado["cantidad_antes"] == 1:
        print(
            f"Errores antes : "
            f"{resultado['cantidad_antes']} "
            f"({fecha_antes})"
        )
    else:
        print(
            f"Errores antes : "
            f"{resultado['cantidad_antes']} "
            f"(el primero: {fecha_antes})"
        )

    # ERRORES DESPUÉS
    if resultado["cantidad_despues"] == 1:
        print(
            f"Errores después: "
            f"{resultado['cantidad_despues']} "
            f"({fecha_despues})"
        )
    else:
        print(
            f"Errores después: "
            f"{resultado['cantidad_despues']} "
            f"(el primero: {fecha_despues})"
        )

    print("Diferencia:", resultado["diferencia"])

    print("\n-----------------------------")
    print("TIPOS ANTES")
    print("-----------------------------")

    imprimir_resumen_errores(
        resultado["tipos_antes"]
    )

    print("\n-----------------------------")
    print("TIPOS DESPUÉS")
    print("-----------------------------")

    imprimir_resumen_errores(
        resultado["tipos_despues"]
    )

    print("\n-----------------------------")
    print("NUEVOS ERRORES")
    print("-----------------------------")

    pprint(resultado["nuevos_errores"])

    print("\n-----------------------------")
    print("ERRORES RESUELTOS")
    print("-----------------------------")

    pprint(resultado["errores_resueltos"])

    print("\n-----------------------------")
    print("RESULTADO FINAL")
    print("-----------------------------")

    if resultado["empeoro"]:
        print("EMPEORÓ")
    elif resultado["mejoro"]:
        print("MEJORÓ")
    else:
        print("QUEDÓ IGUAL")


# =========================================================
# REPORTE COMPLETO
# FLUJO:
# 1. analizar actual
# 2. aplicar cambios externamente
# 3. volver a analizar
# 4. comparar
# =========================================================
def reporte_completo(
    codigo_producto,
    aplicar_cambios_fn=None,
    cambios=None,
    aplicar=False
):

    # =========================================================
    # 1) SNAPSHOT ANTES
    # =========================================================
    resultado_antes = analizar(codigo_producto)
    historial_antes = resultado_antes["historial"]

    analisis_antes = ejecutar_analisis(historial_antes)
    sugerencias_antes = ejecutar_sugerencias(historial_antes)

    # =========================================================
    # 2) APLICAR CAMBIOS (OPCIONAL Y CONTROLADO)
    # =========================================================
    if aplicar and aplicar_cambios_fn and cambios:
        aplicar_cambios_fn(cambios)

    # =========================================================
    # 3) SNAPSHOT DESPUÉS
    # =========================================================
    resultado_despues = analizar(codigo_producto)
    historial_despues = resultado_despues["historial"]

    analisis_despues = ejecutar_analisis(historial_despues)
    sugerencias_despues = ejecutar_sugerencias(historial_despues)

    # =========================================================
    # 4) COMPARACIÓN
    # =========================================================
    comparacion_errores = comparar_errores(
        analisis_antes["errores"],
        analisis_despues["errores"]
    )

    comparacion_sugerencias = comparar_errores(
        sugerencias_antes["sugerencias"],
        sugerencias_despues["sugerencias"]
    )

    # =========================================================
    # OUTPUT
    # =========================================================
    print("\n================================================")
    print("REPORTE COMPLETO")
    print("================================================")

    print("Código:", codigo_producto)

    print("\n--- ERRORES ---")
    imprimir_comparacion(comparacion_errores)

    print("\n--- SUGERENCIAS ---")
    imprimir_comparacion(comparacion_sugerencias)

    return {
        "antes": {
            "errores": analisis_antes,
            "sugerencias": sugerencias_antes
        },
        "despues": {
            "errores": analisis_despues,
            "sugerencias": sugerencias_despues
        },
        "comparacion": {
            "errores": comparacion_errores,
            "sugerencias": comparacion_sugerencias
        }
    }

# REPORTE MASIVO
def reporte_masivo(lista_codigos):

    productos_con_errores = []
    productos_sin_errores = []

    productos_con_sugerencias = []
    productos_sin_sugerencias = []

    for codigo in lista_codigos:

        try:

            resultado = analizar(codigo)

            historial = resultado["historial"]

            errores = ejecutar_analisis(historial)

            sugerencias = ejecutar_sugerencias(historial)

            historial = resultado["historial"]
            errores = ejecutar_analisis(historial)
            if errores["total_errores"] > 0:
                productos_con_errores.append(codigo)
            else:
                productos_sin_errores.append(codigo)
            if errores["total_errores"] > 5:
                print("⚠️ producto crítico")
            
            if sugerencias["total_sugerencias"] > 0:
                productos_con_sugerencias.append(codigo)
            else:
                productos_sin_sugerencias.append(codigo)

        except Exception as ex:

            print("\nERROR GRAVE EN:", codigo)
            raise

    print("\n================================================")
    print("REPORTE MASIVO")
    print("================================================")

    print("\nproductos_con_errores =")
    print(productos_con_errores)

    print("\nproductos_sin_errores =")
    print(productos_sin_errores)

    print("\nproductos_con_sugerencias =")
    print(productos_con_sugerencias)

    print("\nproductos_sin_sugerencias =")
    print(productos_sin_sugerencias)

    print("\n================================================")
    print("TOTALES")
    print("================================================")

    print("cantidad_productos =", len(lista_codigos))

    print(
        "cantidad_productos_con_errores =",
        len(productos_con_errores)
    )

    print(
        "cantidad_productos_sin_errores =",
        len(productos_sin_errores)
    )

    print(
        "cantidad_productos_con_sugerencias =",
        len(productos_con_sugerencias)
    )

    print(
        "cantidad_productos_sin_sugerencias =",
        len(productos_sin_sugerencias)
    )

    return {
        "productos_con_errores": productos_con_errores,
        "productos_sin_errores": productos_sin_errores,
        "productos_con_sugerencias": productos_con_sugerencias,
        "productos_sin_sugerencias": productos_sin_sugerencias
    }


def snapshot(codigo):
    resultado = analizar(codigo)
    historial = resultado["historial"]
    errores = ejecutar_analisis(historial)
    sugerencias = ejecutar_sugerencias(historial)

    return {
        "historial": historial,
        "errores": errores["errores"],
        "sugerencias": sugerencias["sugerencias"]
    }

def ejecutar_pipeline(
    codigo_producto,
    aplicar_cambios_fn=None,
    cambios=None,
    modo_simulacion=False
):

    print("\n================ PIPELINE =================")
    print("Producto:", codigo_producto)

    # =========================================================
    # 1) SNAPSHOT ANTES
    # =========================================================
    resultado_antes = analizar(codigo_producto)
    historial_antes = resultado_antes["historial"]

    errores_antes = ejecutar_analisis(historial_antes)
    sugerencias_antes = ejecutar_sugerencias(historial_antes)

    # =========================================================
    # 2) SIMULACIÓN (NO TOCA DB)
    # =========================================================
    if modo_simulacion:
        print("\n[SIMULACIÓN ACTIVADA - NO SE APLICAN CAMBIOS]")
        aplicar_resultado = None
    else:
        aplicar_resultado = None
        if aplicar_cambios_fn and cambios:
            aplicar_resultado = aplicar_cambios_fn(cambios)

    # =========================================================
    # 3) SNAPSHOT DESPUÉS
    # =========================================================
    resultado_despues = analizar(codigo_producto)
    historial_despues = resultado_despues["historial"]

    errores_despues = ejecutar_analisis(historial_despues)
    sugerencias_despues = ejecutar_sugerencias(historial_despues)

    # =========================================================
    # 4) COMPARACIÓN DE ERRORES
    # =========================================================
    comparacion_errores = comparar_errores(
        errores_antes["errores"],
        errores_despues["errores"]
    )

    # =========================================================
    # 5) COMPARACIÓN DE SUGERENCIAS
    # =========================================================
    comparacion_sugerencias = comparar_errores(
        sugerencias_antes["sugerencias"],
        sugerencias_despues["sugerencias"]
    )

    # =========================================================
    # OUTPUT
    # =========================================================
    print("\n================================================")
    print("PIPELINE RESULTADO")
    print("================================================")

    print("Código:", codigo_producto)

    print("\n--- ERRORES ---")
    imprimir_comparacion(comparacion_errores)

    print("\n--- SUGERENCIAS ---")
    imprimir_comparacion(comparacion_sugerencias)

    return {
        "antes": {
            "errores": errores_antes,
            "sugerencias": sugerencias_antes
        },
        "despues": {
            "errores": errores_despues,
            "sugerencias": sugerencias_despues
        },
        "comparacion": {
            "errores": comparacion_errores,
            "sugerencias": comparacion_sugerencias
        },
        "aplicacion": aplicar_resultado
    }
