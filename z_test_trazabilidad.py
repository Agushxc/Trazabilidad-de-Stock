# z_test_trazabilidad
from pprint import pprint
from a_db import db
from c_motor_trazabilidad import analizar
from d_analizador_errores import ejecutar_analisis
from e_sugeridor_correcciones import ejecutar_sugerencias
from g_reportes import reporte_simple
from f_aplicador_cambios import aplicar_cambios
from k_corrige_errores_iniciales import corregir_errores_iniciales
#from i_simulador import simular_cambios
import sys
import shutil
import subprocess
import os
import re
from datetime import datetime
inicio = datetime.now()
print(f"Comenzó a las {inicio.strftime('%H:%M:%S')}")

DB_ORIGEN = r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\Nueva carpeta (2)\base_de_datos_interna.db"
DB_DESTINO = r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\base_de_datos_interna.db"
EXCEL_SCRIPT = r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\pos_puntopos\trazabilidad de un producto\04_crear_excel_con_un_solo_producto.py"

def obtener_datos(codigo):
    resultado = analizar(codigo)
    historial = resultado["historial"]
    return resultado, historial

def ver_historial(codigo):
    _, historial = obtener_datos(codigo)

    print(
        "fecha_hora".ljust(19),
        "| movimiento".ljust(35),
        "| valor_anterior".ljust(15),
        "| nuevo_valor".ljust(12),
        "| cantidad".ljust(10),
        "| stock"
    )

    print("-" * 120)

    for e in historial:
        print(
            str(e.get("fecha")).ljust(19),
            "|",
            str(e.get("movimiento")).ljust(34),
            "|",
            str(e.get("valor_anterior")).ljust(14),
            "|",
            str(e.get("nuevo_valor")).ljust(11),
            "|",
            str(e.get("cantidad")).ljust(9),
            "|",
            e.get("stock_reconstruido")
        )

def ver_errores(codigo):
    _, historial = obtener_datos(codigo)
    resultado = ejecutar_analisis(historial)
    inconsistencias = resultado["inconsistencias"]
    total = resultado["total_inconsistencias"]

    if total == 0:
        print("Sin errores.")
        return

    print(f"{total} inconsistencia(s):\n")
    for e in inconsistencias:
        det = e.get("detalle", {})
        va = e.get("valor_anterior")
        te1 = e.get("stock_esperado_1")
        dif = e.get("diferencia_1")
        print(
            f"  {det.get('fecha')} | {det.get('movimiento')}"
            f" | anterior: {va} | esperado: {te1} | diferencia: {dif}"
        )

def ver_sugerencias(codigo):
    _, historial = obtener_datos(codigo)
    sugerencias = ejecutar_sugerencias(historial)
    pprint(sugerencias)
def ver_reporte(codigo):
    reporte_simple(codigo)

analisis_count = 0
def proceso_automatico_trazabilidad():
    global analisis_count
    def agregar_sugerencias(sugerencias_por_factura, accionables):
        for s in accionables:

            if s.get("tipo") != "mover_factura":
                continue

            id_factura = s.get("id_factura")

            if not id_factura:
                continue

            fecha_sugerida = s.get("fecha_sugerida")

            actual = sugerencias_por_factura.get(id_factura)

            if (
                actual is None
                or fecha_sugerida < actual["fecha_sugerida"]
            ):
                sugerencias_por_factura[id_factura] = {
                    "id_factura": id_factura,
                    "fecha_original": s.get("fecha_original"),
                    "fecha_sugerida": fecha_sugerida
                }
    
    
    print("\nINICIANDO PROCESO AUTOMÁTICO DE TRAZABILIDAD\n")
    conn = db.conectar()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT codigo FROM productos")

    # cur.execute("""
    #     SELECT DISTINCT codigo
    #     FROM productos
    #     WHERE CAST(codigo AS INTEGER) BETWEEN ? AND ?
    #     ORDER BY CAST(codigo AS INTEGER)
    # """, (2000, 2001))

    codigos = [c[0] for c in cur.fetchall()]
    print(f"Total códigos a procesar: {len(codigos)}")
    sugerencias_por_factura = {}
    for i, codigo in enumerate(codigos, start=1):
        print(f"[{i}/{len(codigos)}] {codigo}")
        print(f"PROCESANDO CÓDIGO: {codigo}")
        analisis_count += 1
        print(f"ANALISIS #{analisis_count} -> {codigo}")
        resultado = analizar(codigo)
        historial = resultado["historial"]

        # VALIDACIÓN SIMPLE DE AISLAMIENTO
        if any(e.get("codigo") not in [None, codigo] for e in historial if isinstance(e, dict)):
            print(f"⚠️ ALERTA: contaminación de historial detectada en {codigo}")

        errores = ejecutar_analisis(historial)
        inconsistencias = errores.get("inconsistencias", errores)

        # CASO 1: sin errores → siguiente código
        if not inconsistencias:
            sugerencias_result = ejecutar_sugerencias(historial)

            agregar_sugerencias(
                sugerencias_por_factura,
                sugerencias_result["sugerencias"]
            )

            continue
        # CASO 2: hasta 3 ciclos completos de analizar/corregir
        restantes = 0

        for intento in range(1, 4):

            if intento > 1:
                print(f"[{i}/{len(codigos)}] {codigo}")
                print(f"PROCESANDO CÓDIGO: {codigo}")
                analisis_count += 1
                print(f"ANALISIS #{analisis_count} -> {codigo}")

                resultado = analizar(codigo)
                historial = resultado["historial"]

                errores = ejecutar_analisis(historial)
                inconsistencias = errores.get("inconsistencias", errores)

            if not inconsistencias:
                print(f"Código {codigo}: inconsistencias resueltas")
                break

            print(f"Código {codigo}: detectadas inconsistencias → aplicando corrección inicial ({intento}/3)")

            restantes = corregir_errores_iniciales(codigo)

            if restantes == 0:
                print(f"Código {codigo}: inconsistencias resueltas")
                break


        # CASO 3
        if inconsistencias and (restantes is None or restantes > 0):
            print(f"Código {codigo}: ERROR PERSISTENTE → activando modo auditoría")

            # 1. copiar DB
            try:
                shutil.copyfile(DB_ORIGEN, DB_DESTINO)
                print("Base de datos copiada correctamente")
            except Exception as e:
                print(f"Error copiando DB: {e}")
                return

            # 2. inyectar código en script Excel
            try:
                with open(EXCEL_SCRIPT, "r", encoding="utf-8") as f:
                    contenido = f.read()

                contenido_modificado = re.sub(
                    r'for\s+codigo\s+in\s+\[".*?"\]',
                    f'for codigo in ["{codigo}"]',
                    contenido
                )

                with open(EXCEL_SCRIPT, "w", encoding="utf-8") as f:
                    f.write(contenido_modificado)

            except Exception as e:
                print(f"Error modificando script Excel: {e}")
                return

            # 3. ejecutar script
            try:
                subprocess.run(["python", EXCEL_SCRIPT], check=True)
            except Exception as e:
                print(f"Error ejecutando Excel script: {e}")
                return

            print(f"el código {codigo} contiene un error que no pudo ser resuelto")
            mensaje_a_decir = f"el código {codigo} contiene un error que no pudo ser resuelto, ya se hizo el excel y se abrió para que lo veas."
            def hablar():
                try:
                    import asyncio
                    import edge_tts
                    import tempfile
                    import os
                    from playsound import playsound
                except ImportError as e:
                    faltante = str(e).split("'")[1] if "'" in str(e) else "dependencias"

                    print("⚠️ VOZ DESACTIVADA")
                    print(f"Falta instalar: {faltante}")
                    print("💡 Ejecuta: pip install edge-tts playsound")
                    return

                async def _run():
                    voz = "es-UY-ValentinaNeural"

                    communicate = edge_tts.Communicate(mensaje_a_decir, voz)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        path = f.name

                    await communicate.save(path)
                    playsound(path)
                    os.remove(path)

                try:
                    asyncio.run(_run())
                except Exception as e:
                    print("⚠️ Error en sistema de voz:", e)
            hablar()
            return
    print("\nAGRUPACIÓN FINALIZADA")
    print(
        f"Facturas candidatas: "
        f"{len(sugerencias_por_factura)}"
    )

    cambios = [
        {
            "tipo": "mover_factura",
            "id_factura": dato["id_factura"],
            "fecha_sugerida": dato["fecha_sugerida"]
        }
        for dato in sugerencias_por_factura.values()
    ]

    cambios.sort(key=lambda x: x["fecha_sugerida"])

    for cambio in cambios:
        print(
            f"factura={cambio['id_factura']} "
            f"-> {cambio['fecha_sugerida']}"
        )

    if cambios:
        aplicar_cambios(cambios)
    # subprocess.Popen([sys.executable,
    #     r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\pos_puntopos\trazabilidad de un producto\04_imprime_diagnostico_completo.py"
    # ])

    mensaje_a_decir = "Listo, se ejecutó todo y no quedaron errores de inconsistencia en ningún código... re bien!"
    def hablar():
        try:
            import asyncio
            import edge_tts
            import tempfile
            import os
            from playsound import playsound
        except ImportError as e:
            faltante = str(e).split("'")[1] if "'" in str(e) else "dependencias"

            print("⚠️ VOZ DESACTIVADA")
            print(f"Falta instalar: {faltante}")
            print("💡 Ejecuta: pip install edge-tts playsound")
            return

        async def _run():
            voz = "es-UY-ValentinaNeural"

            communicate = edge_tts.Communicate(mensaje_a_decir, voz)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                path = f.name

            await communicate.save(path)
            playsound(path)
            os.remove(path)

        try:
            asyncio.run(_run())
        except Exception as e:
            print("⚠️ Error en sistema de voz:", e)
    hablar()
    # FIN
    fin = datetime.now()
    print(f"Terminó a las {fin.strftime('%H:%M:%S')}")

    # DIFERENCIA
    delta = fin - inicio

    horas = delta.seconds // 3600
    minutos = (delta.seconds % 3600) // 60
    segundos = delta.seconds % 60

    if horas > 0:
        print(f"Tardó {horas} horas, {minutos} minutos y {segundos} segundos")
    else:
        print(f"Tardó {minutos} minutos y {segundos} segundos")

def aplicar(codigo):
    _, historial = obtener_datos(codigo)
    sugerencias = ejecutar_sugerencias(historial)

    if not sugerencias["sugerencias"]:
        print(f"codigo: {codigo} sin sugerencia de corrección")
        if sugerencias.get("total_revision_manual", 0) > 0:
            print(f"  ({sugerencias['total_revision_manual']} caso(s) requieren revisión manual)")
        return

    for _ in range(10):
        _, historial = obtener_datos(codigo)
        sugerencias_result = ejecutar_sugerencias(historial)
        accionables = sugerencias_result["sugerencias"]

        if not accionables:
            print(f"Código {codigo}: sin más sugerencias accionables")
            break

        print(f"Código {codigo}: aplicando sugerencia ({len(accionables)} restante(s))")
        aplicar_cambios([accionables[0]])

def buscar_primero_con_sugerencias():
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT codigo FROM productos")
    codigos = [c[0] for c in cur.fetchall()]

    for codigo in codigos:
        _, historial = obtener_datos(codigo)
        sugerencias_result = ejecutar_sugerencias(historial)

        if sugerencias_result["sugerencias"]:
            print(f"Primer código con sugerencias: {codigo}")
            print(f"  → {len(sugerencias_result['sugerencias'])} sugerencia(s) accionable(s)")
            aplicar(codigo)  # ← ya usa el loop interno
            return

    print("Ningún código tiene sugerencias accionables.")

def diagnostico_base(ruta_db):
    import a_db as _db_module

    # guardar ruta actual y apuntar a la nueva
    ruta_original = _db_module.db_file
    _db_module.db_file = ruta_db

    # forzar reconexión con la nueva ruta
    _db_module.db.cerrar()

    conn = _db_module.db.conectar()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT codigo FROM productos")
    codigos = [c[0] for c in cur.fetchall()]

    total_errores = 0
    total_sugerencias = 0
    codigos_con_errores = 0
    codigos_con_sugerencias = 0

    for i, codigo in enumerate(codigos):
        print(f"  analizando {i+1}/{len(codigos)}...", end="\r")
        resultado = analizar(codigo)
        historial = resultado["historial"]

        errores = ejecutar_analisis(historial)
        inconsistencias = errores.get("inconsistencias", [])
        if inconsistencias:
            total_errores += len(inconsistencias)
            codigos_con_errores += 1

        sugerencias_result = ejecutar_sugerencias(historial)
        accionables = sugerencias_result["sugerencias"]
        if accionables:
            total_sugerencias += len(accionables)
            codigos_con_sugerencias += 1

    # restaurar ruta original
    _db_module.db_file = ruta_original
    _db_module.db.cerrar()
    _db_module.db.conectar()

    print(f"\n{'='*40}")
    print(f"DIAGNÓSTICO: {ruta_db}")
    print(f"{'='*40}")
    print(f"Códigos analizados:       {len(codigos)}")
    print(f"Códigos con errores:      {codigos_con_errores}  ({total_errores} totales)")
    print(f"Códigos con sugerencias:  {codigos_con_sugerencias}  ({total_sugerencias} totales)")
    print(f"{'='*40}\n")

def diagnostico_detallado(codigo):
    _, historial = obtener_datos(codigo)
    
    # errores
    errores = ejecutar_analisis(historial)
    inconsistencias = errores.get("inconsistencias", [])
    
    # sugerencias
    sugerencias_result = ejecutar_sugerencias(historial)
    accionables = sugerencias_result["sugerencias"]
    revision = sugerencias_result.get("revision_manual", [])

    print(f"\n{'='*50}")
    print(f"DIAGNÓSTICO DETALLADO: {codigo}")
    print(f"{'='*50}")
    print(f"Inconsistencias: {len(inconsistencias)}")
    for inc in inconsistencias:
        det = inc.get("detalle", {})
        print(f"  {det.get('fecha')} | {det.get('movimiento')} | dif: {inc.get('diferencia_1')}")

    print(f"\nSugerencias accionables: {len(accionables)}")
    for s in accionables:
        print(f"  factura={s.get('id_factura')} | {s.get('fecha_original')} → {s.get('fecha_sugerida')}")
        print(f"  stock negativo: {s.get('stock_negativo')} desde {s.get('fecha_inicio_negativo')}")

    print(f"\nRevisión manual: {len(revision)}")
    for r in revision:
        print(f"  desde {r.get('fecha_inicio_negativo')} | stock: {r.get('stock_negativo')}")

    print(f"\nHistorial completo:")
    for e in historial:
        marca = " ←" if float(e.get("stock_reconstruido") or 0) < 0 else ""
        print(f"  {e.get('fecha')} | {e.get('movimiento')} | cant: {e.get('cantidad')} | stock: {e.get('stock_reconstruido')}{marca}")

# MENÚ
def menu():
    codigo = input("Código de producto: ")

    while True:
        print("""
========================
MENÚ TRAZABILIDAD
========================
1 - ver historial
2 - ver errores
3 - ver sugerencias
4 - reporte simple
5 - simulación
6 - aplicar cambios
7 - corregir errores iniciales
8 - cambiar código
9 - proceso automático de trazabilidad
10 - buscar primero con sugerencias y aplicar
11 - comparación del antes y después de cambiar fechas
12 - diagnostico detallado
0 - salir

""")

        op = input("Opción: ")

        if op == "1":
            ver_historial(codigo)

        elif op == "2":
            ver_errores(codigo)

        elif op == "3":
            ver_sugerencias(codigo)

        elif op == "4":
            ver_reporte(codigo)

        # elif op == "5":
        #     simular(codigo)

        elif op == "6":
            aplicar(codigo)

        elif op == "7":
            corregir_errores_iniciales(codigo)

        elif op == "8":
            codigo = input("Nuevo código de producto: ")

        elif op == "9":
            proceso_automatico_trazabilidad()

        elif op == "10":
            buscar_primero_con_sugerencias()

        elif op == "11":
            print("1 - DB vieja (antes de cambios)")
            print("2 - DB nueva (después de cambios)")
            eleccion = input("Elegí: ")
            if eleccion == "1":
                diagnostico_base(r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\Nueva carpeta (2)\base_de_datos_interna.db")
            elif eleccion == "2":
                diagnostico_base(r"C:\Users\agus_\OneDrive\All-In-One Workspace VSC\Nueva carpeta (3)\base_de_datos_interna.db")

        elif op == "12":
            diagnostico_detallado(codigo)



        elif op == "0":
            break

# ENTRY POINT
if __name__ == "__main__":
    menu()