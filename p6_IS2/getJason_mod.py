#!/usr/bin/env python3
"""
Módulo: getJason_mod.py
Descripción: Recupera de forma dinámica tokens y claves múltiples desde un repositorio JSON.
Cátedra: Ingeniería de Software II (FCYT-UADER)
Requerimiento: El archivo queda prefijado y la clave se pasa opcionalmente por consola.
"""

import json
import sys

def main():
    """
    Función principal que implementa la lógica de extracción parametrizada
    con fallback seguro al token por defecto.
    """
    # Se establece de manera estática el archivo de datos del negocio
    jsonfile = "sitedata.json"
    
    # REQUERIMIENTO: Si el usuario ingresa un argumento, se toma como la clave a buscar.
    # Si la lista de argumentos está vacía, se asigna "token1" por defecto.
    if len(sys.argv) > 1:
        jsonkey = sys.argv[1]
    else:
        jsonkey = "token1"

    try:
        # Intenta abrir el repositorio JSON local en modo lectura
        with open(jsonfile, "r") as myfile:
            data = myfile.read()
        
        # Parsea la cadena de texto plana a un diccionario de Python
        obj = json.loads(data)
        
        # Validación: Comprueba si la clave solicitada existe dentro del diccionario
        if jsonkey in obj:
            print(str(obj[jsonkey]))
        else:
            print(f"Error: La clave '{jsonkey}' no fue encontrada en {jsonfile}.")
            sys.exit(1)
            
    # Bloque de captura de excepciones para asegurar la estabilidad del sistema
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo obligatorio '{jsonfile}'.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo '{jsonfile}' no contiene un formato JSON válido.")
        sys.exit(1)

if __name__ == "__main__":
    main()
