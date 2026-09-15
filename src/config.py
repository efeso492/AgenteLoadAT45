from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from typing import Any
import pyodbc



logger = logging.getLogger(__name__)


def leer_configuracion() -> dict[str, Any]:
    """
    Lee el archivo de configuración y devuelve su contenido.

    Returns:
        dict[str, Any]: Configuración cargada desde conf.json.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el contenido JSON es inválido.
    """
    respConfig = {}

    ruta_configuracion = (Path(__file__).resolve().parent.parent / "conf" / "conf.json")
    ruta_logs          = Path(__file__).resolve().parent.parent / "logs"
    ruta_inputs        = Path(__file__).resolve().parent.parent / "inputs"
    ruta_process       = Path(__file__).resolve().parent.parent / "process"
    ruta_queries       = Path(__file__).resolve().parent.parent / "queris"    

    try:
        with ruta_configuracion.open( mode="r",encoding="utf-8") as archivo:
            configuracion = json.load(archivo)
       
        logger.info("Configuración cargada correctamente desde %s",
            ruta_configuracion)


        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                RotatingFileHandler(
                    os.path.join(ruta_logs,configuracion['logFile_Name']),
                    maxBytes = configuracion["logFile_MaxSize"],
                    backupCount = configuracion["backupCount"]
                ),
                logging.StreamHandler()
            ]
        )

        respConfig                 = configuracion
        respConfig["logs"]         = logging
        connection_string          = "DRIVER={SQL Server};"f"SERVER={configuracion['SERVER']};"f"DATABASE={configuracion['DATABASE']};"f"Trusted_Connection=yes;"
        respConfig["conexion"]     = pyodbc.connect(connection_string)
        respConfig["ruta_inputs"]  = ruta_inputs
        respConfig["ruta_process"] = ruta_process
        queries_data={} 

        list_queries = os.listdir(ruta_queries)
        
        for query in list_queries: 
            q_name, __ = query.split(".")
            if not query in respConfig["list_queries"]:
                logging.error(f"==> Consulta SQL -- {q_name} -- no se encuentra en el directorio, por favor revise el directorio {ruta_queries} y el archivo de confirugración") 
                exit(1)
            else:
                with open(os.path.join(ruta_queries, query), "r") as f:
                    query = f.read() 
                    f.close()             
                    if query  : 
                        queries_data[q_name] = query
                    else:  
                        logging.error(f"==> SQL file  '{query}' it's empty.") 
                        logging.error("==> Process aborted...")
                        exit(1)                

        respConfig["queries_data"] = queries_data   


        return respConfig

    except FileNotFoundError:
        logger.exception(
            "No existe el archivo de configuración: %s",
            ruta_configuracion
        )
        raise

    except json.JSONDecodeError as exc:
        logger.exception("Error al parsear el archivo JSON: %s",ruta_configuracion)    
        raise ValueError(f"JSON inválido en {ruta_configuracion}") from exc


