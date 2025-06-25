def clean_json_response(response: str) -> str:
    """
    Limpia delimitadores de bloque de código (``` o ```json) de una respuesta de IA para dejar solo el JSON puro.
    """
    lines = response.strip().splitlines()
    # Filtra líneas que no empiezan por ```
    cleaned = [line for line in lines if not line.strip().startswith('```')]
    return '\n'.join(cleaned).strip()
