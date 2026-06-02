#!/usr/bin/env python3
"""
Módulo: getJason_mod.py
Descripción: Recupera de forma dinámica tokens y claves múltiples desde un 
             repositorio JSON utilizando el patrón de diseño Singleton.
Cátedra: Ingeniería de Software II (FCYT-UADER)
Licencia: copyright UADER-FCyT-IS2©2024 todos los derechos reservados

Este programa ha sido re-factorizado para incorporar POO, garantizar que
nunca falle con excepciones del sistema no controladas y soportar flags de versión.
"""

import json
import sys


class JSONTokenReader:
    """
    Clase que implementa el patrón Singleton para gestionar la lectura
    centralizada y única de la configuración desde un archivo JSON.
    """
    _instance = None
    _data = None

    def __new__(cls, *args, **kwargs):
        """
        Garantiza que exista una única instancia de la clase en memoria.
        """
        if cls._instance is None:
            cls._instance = super(JSONTokenReader, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename="sitedata.json"):
        """
        Inicializa la instancia cargando los datos si aún no han sido procesados.
        """
        # Evita recargar el archivo si la instancia ya fue inicializada previamente
        if self._data is None:
            self._filename = filename
            self._load_data()

    def _load_data(self):
        """
        Carga y parsea el archivo JSON de forma segura. Controla los errores
        para que el sistema nunca lance una excepción cruda del lenguaje.
        """
        try:
            with open(self._filename, "r", encoding="utf-8") as myfile:
                content = myfile.read()
            self._data = json.loads(content)
        except FileNotFoundError:
            print(f"Error del programa: No se pudo encontrar el archivo "
                  f"obligatorio '{self._filename}'.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error del programa: El archivo '{self._filename}' "
                  f"no contiene un formato JSON válido.")
            sys.exit(1)
        except PermissionError:
            print(f"Error del programa: Permisos insuficientes para leer "
                  f"'{self._filename}'.")
            sys.exit(1)

    def get_token(self, key):
        """
        Recupera el valor asociado a una clave. Si no existe, finaliza
        con un error controlado.
        """
        if self._data is not None and key in self._data:
            return str(self._data[key])
        
        print(f"Error del programa: La clave '{key}' no fue encontrada "
              f"en {self._filename}.")
        sys.exit(1)


def parse_arguments():
    """
    Valida y procesa los argumentos de la línea de comandos de forma robusta.
    Evita la terminación abrupta por excepciones del lenguaje.
    """
    # Si hay más de un parámetro, el uso es incorrecto
    if len(sys.argv) > 2:
        print("Error del programa: Demasiados argumentos. "
              "Uso: python getJason_mod.py [clave | -v]")
        sys.exit(1)

    # Si no se pasan argumentos, se usa el token por defecto
    if len(sys.argv) == 1:
        return "token1"

    argument = sys.argv[1]

    # Requerimiento g): Control de flag de versión
    if argument == "-v":
        print("versión 1.1")
        sys.exit(0)

    # Control de argumentos inválidos (ej. flags vacíos o extraños si se requiriera)
    if not argument.strip():
        print("Error del programa: El argumento provisto no puede estar vacío.")
        sys.exit(1)

    return argument


def main():
    """
    Función principal. Coordina la ejecución aplicando Branching by Abstraction:
    la lógica de negocio interactúa con la capa abstracta/clase Singleton en lugar
    de manipular directamente accesos a archivos o diccionarios globales.
    """
    # 1. Validación robusta de argumentos de entrada
    json_key = parse_arguments()

    # 2. Instanciación e interacción con el Singleton
    reader = JSONTokenReader("sitedata.json")
    token_value = reader.get_token(json_key)

    # 3. Salida estándar del resultado
    print(token_value)


if __name__ == "__main__":
    main()