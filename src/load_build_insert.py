from __future__ import annotations
from pathlib import Path
from typing import Any
import pyodbc


def ejecutar_bulk_insert(config: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta el bulk insert en la tabla At45_Staging."""
    resultado    = {"status": False, "message": ""}
    logs         = config["logs"]
    conexion     = config["conexion"]
    sql          = config["queries_data"]["bulk_insert_At45"]
    sql_count    = config["queries_data"]["count_At45_Stagins"]
    ruta_input   = Path(__file__).resolve().parent.parent / "inputs" 
    cursor       = conexion.cursor()
    archivos = [ archivo for archivo in ruta_input.iterdir() if archivo.is_file()]


    if len(archivos) == 0:
            resultado["message"] = ("No hay archivos en la carpeta inputs")
            logs.warning(resultado["message"])
            return resultado
    
    elif len(archivos) > 1:
            resultado["message"] = ("Hay más de un archivo en la carpeta inputs")
            logs.warning(resultado["message"])
            return resultado

    ruta_archivo = archivos[0]
    logs.info("Archivo encontrado: %s", ruta_archivo.name)

    try:

        if cursor:
            logs.info("Conexión exitosa")
            sql = sql.format(ruta_archivo=ruta_archivo.as_posix())
            cursor.execute(sql)
            cursor.execute(sql_count)
            count = cursor.fetchone()[0]

        if count == 0:
            raise RuntimeError("La tabla At45_Staging quedó vacía después del BULK INSERT")                
        
        conexion.commit()
        logs.info("Validación exitosa. Registros cargados: %s",count)
        logs.info("Proceso completado")
        resultado["status"] = True
        resultado["message"] = "At45_Staging procesada exitosamente"
        return resultado

    except Exception as error:
        conexion.rollback()
        resultado["status"] = False
        resultado["message"] = str(error)
        logs.exception("Error al procesar At45_Staging: %s",error)
        return resultado
    finally:
        cursor.close()
    return resultado    