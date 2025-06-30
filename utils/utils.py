import demjson3


def clean_json_response(response: str) -> str:
    """
    Limpia delimitadores de bloque de código (``` o ```json) de una respuesta de IA para dejar solo el JSON puro.
    Además, utiliza demjson3 para corregir y validar el JSON resultante.
    """
    # Asegurarse de que la respuesta sea una cadena
    if not isinstance(response, str):
        response = str(response)

    # Reemplazar valores booleanos de Python por valores JSON válidos
    response = response.replace('True', 'true').replace('False', 'false')

    # Usa demjson3 para corregir y validar el JSON directamente
    try:
        corrected_json = demjson3.decode(response)
        return demjson3.encode(corrected_json)
    except demjson3.JSONDecodeError as e:
        # Debug: Log the exact error and position
        print("JSON validation error:", e)
        print("Problematic JSON:", response)
        raise ValueError(f"La respuesta limpiada no es un JSON válido: {e}")
