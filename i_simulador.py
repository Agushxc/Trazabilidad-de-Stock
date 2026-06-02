# i_simulador.py

from copy import deepcopy
from j_reconstructor import ejecutar_reconstruccion
from h_validadores import ejecutar_validaciones
from d_analizador_errores import ejecutar_analisis
from e_sugeridor_correcciones import ejecutar_sugerencias


# =========================================================
# UTILIDAD
# =========================================================

def copiar_historial(resultado_reconstruccion):

    return deepcopy(
        resultado_reconstruccion.get(
            "historial",
            []
        )
    )


def obtener_tipos(lista):

    resumen = {}

    for e in lista:

        tipo = e.get("tipo")

        resumen[tipo] = (
            resumen.get(tipo, 0) + 1
        )

    return resumen


def calcular_diferencia(
    antes,
    despues
):

    return despues - antes


# =========================================================
# GENERAR ESTADO COMPLETO
# =========================================================

def generar_estado_producto(codigo):

    reconstruccion = ejecutar_reconstruccion(
        codigo
    )

    historial = copiar_historial(
        reconstruccion
    )

    validaciones = ejecutar_validaciones(
        historial
    )

    errores = ejecutar_analisis(
        historial
    )

    sugerencias = ejecutar_sugerencias(
        historial
    )

    return {

        # BASE
        "codigo": codigo,
        "historial": historial,
        "stock_final": reconstruccion.get(
            "stock_final"
        ),

        # VALIDACIONES
        "validaciones": validaciones,
        "total_inconsistencias": (
            validaciones.get(
                "total_inconsistencias",
                0
            )
        ),

        # ERRORES
        "errores": errores,
        "total_errores": (
            errores.get(
                "total_errores",
                0
            )
        ),

        # SUGERENCIAS
        "sugerencias": sugerencias,
        "total_sugerencias": (
            sugerencias.get(
                "total_sugerencias",
                0
            )
        )
    }


# =========================================================
# COMPARACIÓN
# =========================================================

def comparar_estados(
    antes,
    despues
):

    inconsistencias_antes = (
        antes["total_inconsistencias"]
    )

    inconsistencias_despues = (
        despues["total_inconsistencias"]
    )

    errores_antes = (
        antes["total_errores"]
    )

    errores_despues = (
        despues["total_errores"]
    )

    sugerencias_antes = (
        antes["total_sugerencias"]
    )

    sugerencias_despues = (
        despues["total_sugerencias"]
    )

    return {

        # INCONSISTENCIAS
        "inconsistencias_antes":
            inconsistencias_antes,

        "inconsistencias_despues":
            inconsistencias_despues,

        "diferencia_inconsistencias":
            calcular_diferencia(
                inconsistencias_antes,
                inconsistencias_despues
            ),

        # ERRORES
        "errores_antes":
            errores_antes,

        "errores_despues":
            errores_despues,

        "diferencia_errores":
            calcular_diferencia(
                errores_antes,
                errores_despues
            ),

        # SUGERENCIAS
        "sugerencias_antes":
            sugerencias_antes,

        "sugerencias_despues":
            sugerencias_despues,

        "diferencia_sugerencias":
            calcular_diferencia(
                sugerencias_antes,
                sugerencias_despues
            ),

        # RESÚMENES
        "tipos_inconsistencias_antes":
            obtener_tipos(
                antes["validaciones"][
                    "inconsistencias"
                ]
            ),

        "tipos_inconsistencias_despues":
            obtener_tipos(
                despues["validaciones"][
                    "inconsistencias"
                ]
            ),

        "tipos_errores_antes":
            obtener_tipos(
                antes["errores"][
                    "errores"
                ]
            ),

        "tipos_errores_despues":
            obtener_tipos(
                despues["errores"][
                    "errores"
                ]
            ),

        "tipos_sugerencias_antes":
            obtener_tipos(
                antes["sugerencias"][
                    "sugerencias"
                ]
            ),

        "tipos_sugerencias_despues":
            obtener_tipos(
                despues["sugerencias"][
                    "sugerencias"
                ]
            )
    }


# =========================================================
# SIMULAR CAMBIO
# =========================================================

def simular_producto(
    codigo,
    funcion_aplicadora=None
):

    # -----------------------------------------
    # ESTADO ANTES
    # -----------------------------------------

    antes = generar_estado_producto(
        codigo
    )

    # -----------------------------------------
    # APLICAR SIMULACIÓN
    # -----------------------------------------

    if funcion_aplicadora:

        funcion_aplicadora()

    # -----------------------------------------
    # ESTADO DESPUÉS
    # -----------------------------------------

    despues = generar_estado_producto(
        codigo
    )

    # -----------------------------------------
    # COMPARAR
    # -----------------------------------------

    comparacion = comparar_estados(
        antes,
        despues
    )

    return {

        "codigo": codigo,

        "antes": antes,
        "despues": despues,

        "comparacion": comparacion
    }


# =========================================================
# SIMULAR MUCHOS PRODUCTOS
# =========================================================

def simular_productos(
    codigos,
    funcion_aplicadora=None
):

    resultados = {}

    for codigo in codigos:

        try:

            resultados[codigo] = (
                simular_producto(
                    codigo,
                    funcion_aplicadora
                )
            )

        except Exception as e:

            resultados[codigo] = {
                "error": str(e)
            }

    return resultados


# =========================================================
# RESUMEN GLOBAL
# =========================================================

def generar_resumen_global(
    resultados
):

    resumen = {

        "productos_total": 0,

        "productos_mejoraron": 0,
        "productos_empeoraron": 0,
        "productos_igual": 0,

        "inconsistencias_antes": 0,
        "inconsistencias_despues": 0,

        "errores_antes": 0,
        "errores_despues": 0,

        "sugerencias_antes": 0,
        "sugerencias_despues": 0
    }

    for codigo, r in resultados.items():

        if "comparacion" not in r:
            continue

        c = r["comparacion"]

        resumen["productos_total"] += 1

        # ---------------------------------
        # INCONSISTENCIAS
        # ---------------------------------

        ia = c["inconsistencias_antes"]
        idp = c["inconsistencias_despues"]

        resumen["inconsistencias_antes"] += ia
        resumen["inconsistencias_despues"] += idp

        # ---------------------------------
        # ERRORES
        # ---------------------------------

        ea = c["errores_antes"]
        ed = c["errores_despues"]

        resumen["errores_antes"] += ea
        resumen["errores_despues"] += ed

        # ---------------------------------
        # SUGERENCIAS
        # ---------------------------------

        sa = c["sugerencias_antes"]
        sd = c["sugerencias_despues"]

        resumen["sugerencias_antes"] += sa
        resumen["sugerencias_despues"] += sd

        # ---------------------------------
        # RESULTADO
        # ---------------------------------

        diferencia_total = (
            (idp + ed)
            -
            (ia + ea)
        )

        if diferencia_total < 0:

            resumen["productos_mejoraron"] += 1

        elif diferencia_total > 0:

            resumen["productos_empeoraron"] += 1

        else:

            resumen["productos_igual"] += 1

    return resumen


# =========================================================
# API SIMPLE
# =========================================================

def ejecutar_simulacion(
    codigo,
    funcion_aplicadora=None
):

    return simular_producto(
        codigo,
        funcion_aplicadora
    )