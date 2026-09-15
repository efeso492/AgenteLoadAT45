from __future__ import annotations
from itertools import count
from pathlib import Path
from typing import Any
import pyodbc


def procedure(config: dict[str, Any]) -> dict[str, Any]:
    """
    Ejecuta el procedimiento almacenado encargado de
    procesar la información de At45_Staging hacia At45.

    Args:
        config: Configuración de la aplicación.

    Returns:
        dict[str, Any]: Resultado del proceso.
    """
    resultado = {
        "status": False,
        "message": ""
    }

    logs     = config["logs"]
    conexion = config["conexion"]
    sql      = config["queries_data"]["procedure"]

    cursor = conexion.cursor()

    try:
        logs.info("Conexión exitosa")
        logs.info("Ejecutando procedimiento almacenado")
        cursor.execute(sql)
        conexion.commit()
        logs.info("Procedimiento ejecutado exitosamente")
        resultado["status"] = True
        resultado["message"] = (
            "Procedimiento At45 ejecutado exitosamente"
        )

    except Exception as error:
        conexion.rollback()
        resultado["status"] = False
        resultado["message"] = str(error)
        logs.exception(
            "Error al ejecutar procedimiento At45: %s",
            error
        )

    finally:
        cursor.close()

    return resultado

