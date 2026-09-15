from __future__ import annotations
from typing import Any
import pyodbc


def limpiar_staging(config: dict[str, Any]) -> dict[str, Any]:
    """Limpia la tabla At45_Staging y valida el resultado."""
    resultado    = {"status": False, "message": ""}
    logs         = config["logs"]
    conexion     = config["conexion"]
    sql          = config["queries_data"]["insert_into_At45_Stagins"]
    sql_count    = config["queries_data"]["count_At45_Stagins"]
    cursor       = conexion.cursor()

    try:
        logs.info("Conexión exitosa")
        cursor.execute(sql)
        cursor.execute(sql_count)
        count = cursor.fetchone()[0]

        if count != 0:
            resultado["message"] = "La tabla At45_Staging no quedó vacía"
            raise RuntimeError(resultado["message"])

        conexion.commit()
        logs.info("Validación de limpieza At45_Staging. Registros encontrados: %d", count)
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