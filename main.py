
import logging
from pathlib import Path
import shutil
from tabnanny import check
from typing import Optional
import pyodbc

from src.config             import leer_configuracion
from src.conexion           import limpiar_staging
from src.load_build_insert  import ejecutar_bulk_insert
from src.procedure          import procedure
from src.auditoria          import calcular_checksum, calcular_metadatos_archivo

config = leer_configuracion()

logs= config["logs"]
logs.info("Iniciando la conexión a la base de datos...")
checking =calcular_metadatos_archivo(config)
print(checking)
exit()


limpiar_staging(config)
ejecutar_bulk_insert(config)
procedure(config)