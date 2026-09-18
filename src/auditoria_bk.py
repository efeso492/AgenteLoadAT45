from pathlib import Path
from hashlib import sha256
from datetime import datetime



def calcular_checksum(config: dict) -> str:
    """
    Calcula el checksum SHA256 del archivo contenido
    en la carpeta configurada.

    Args:
        config: Diccionario de configuración que debe
            contener la clave 'ruta_inputs'.

    Returns:
        Hash SHA256 en formato hexadecimal.

    Raises:
        KeyError: Si no existe la clave 'ruta_inputs'.
        FileNotFoundError: Si la carpeta no existe.
        ValueError: Si no se encuentran archivos.
    """
   
    logs = config["logs"]

    try:
        ruta_inputs = Path(config["ruta_inputs"])

        if not ruta_inputs.exists():
            raise FileNotFoundError(
                f"La ruta no existe: {ruta_inputs}"
            )

        archivos = sorted(archivo for archivo in ruta_inputs.iterdir() if archivo.is_file())

        if not archivos:
            raise ValueError(
                f"No se encontraron archivos en {ruta_inputs}"
            )

        archivo_procesar = archivos[0]

        logs.info(
            "Calculando checksum para: %s",
            archivo_procesar.name
        )

        hash_sha256 = sha256()

        with archivo_procesar.open("rb") as archivo:
            for bloque in iter(
                lambda: archivo.read(4096),
                b""
            ):
                hash_sha256.update(bloque)

        return hash_sha256.hexdigest()

    except KeyError:
        logs.exception("Falta la configuración de la ruta de entrada")
        raise
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
        logs.exception("Error accediendo a la ruta o archivo de entrada")
        raise
    except ValueError:
        logs.exception("No se pudo calcular el checksum")
        raise

def calcular_metadatos_archivo(config: dict) -> dict:

    metadatos = {
                "nombre_archivo": "",
                "ruta_archivo": "",
                "tamano_bytes": "",
                "checksum_sha256" : "",
                "fecha_modificacion": "",
                "fecha_carga": "",
                "registros_cargados": "",
                "estado": "fallido",
                "observacion": ""
            }
    """
    Calcula los metadatos del archivo contenido
    en la carpeta configurada.

    Args:
        config: Diccionario de configuración que debe
            contener la clave 'ruta_inputs'.

    Returns:
        Diccionario con metadatos del archivo.

    Raises:
        KeyError: Si no existe la clave 'ruta_inputs'.
        FileNotFoundError: Si la carpeta no existe.
        ValueError: Si no se encuentran archivos.
    """
    logs = config["logs"]

    try:
        ruta_inputs = Path(config["ruta_inputs"])

        if not ruta_inputs.exists():
            raise FileNotFoundError(f"La ruta no existe: {ruta_inputs}")

        archivos = sorted(archivo for archivo in ruta_inputs.iterdir() if archivo.is_file())

        if not archivos:
            raise ValueError(f"No se encontraron archivos en {ruta_inputs}")

        archivo_procesar = archivos[0]

        if archivo_procesar.suffix.lower() != ".txt":
            raise ValueError(
                f"Se esperaba un archivo TXT y se recibió: {archivo_procesar.name}")
        else:
            logs.info("Archivo TXT encontrado: %s",archivo_procesar.suffix)
            metadatos["estado"] = "exitoso"     

        total_registros = sum(1 for _ in archivo_procesar.open(mode="r",encoding="utf-8"))
        logs.info("Total de registros en %s: %d", archivo_procesar.name, total_registros)

        logs.info(
            "Calculando metadatos para: %s",
            archivo_procesar.name
        )

        fecha_modificacion = datetime.fromtimestamp(archivo_procesar.stat().st_mtime)

        metadatos = {
            "nombre_archivo"     : archivo_procesar.name,
            "ruta_archivo"       : str(archivo_procesar),
            "tamano_bytes"       : archivo_procesar.stat().st_size,
            "checksum_sha256"    : calcular_checksum(config),
            "fecha_modificacion" : fecha_modificacion,
            "fecha_carga"        : datetime.now(),
            "registros_cargados" : total_registros,
            "estado"             : metadatos["estado"],
            "observacion"        : ""
        }

        return metadatos

    except KeyError:
        logs.exception("Falta la configuración de la ruta de entrada")
        raise
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
        logs.exception("Error accediendo a la ruta o archivo de entrada")
        raise
    except ValueError:
        logs.exception("No se pudieron calcular los metadatos del archivo")
        raise    


def insertar_auditoria(config: dict, metadatos: dict) -> None:
    """Valida e inserta los metadatos del archivo en la auditoría."""
    conexion = config["conexion"]
    logs     = config["logs"]
    cursor   = conexion.cursor()

    try:
        cursor.execute(
            config["queries_data"]["validar_auditoria"],
            metadatos["checksum_sha256"],
            metadatos["nombre_archivo"],
        )

        if cursor.fetchone() is not None:
            mensaje = (
                "El archivo ya fue cargado anteriormente: "
                f"{metadatos['nombre_archivo']}"
            )
            logs.error(mensaje)
            raise RuntimeError(mensaje)

        cursor.execute(
            config["queries_data"]["insert_auditoria"],
            metadatos["nombre_archivo"],
            metadatos["ruta_archivo"],
            metadatos["tamano_bytes"],
            metadatos["checksum_sha256"],
            metadatos["fecha_modificacion"],
            metadatos["fecha_carga"],
            metadatos["registros_cargados"],
            metadatos["estado"],
            metadatos["observacion"],
        )
        conexion.commit()
        logs.info(
            "Auditoría insertada para el archivo %s",
            metadatos["nombre_archivo"],
        )
    except Exception:
        conexion.rollback()
        logs.exception("Error insertando los metadatos de auditoría")
        raise
    finally:
        cursor.close()
