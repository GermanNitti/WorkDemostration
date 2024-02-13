from bs4 import BeautifulSoup
import json

# Supongamos que 'html_content' contiene el HTML de tu página
html_content = """
<html>
    <template data-type='json' data-varname='__STATE__'>
        <script>
            {"key": "value", "another_key": "another_value"}
        </script>
    </template>
</html>
"""

# Parsea el HTML con BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Encuentra el elemento script dentro del template con los atributos especificados
script_element = soup.select_one("template[data-type='json'][data-varname='__STATE__'] script")

# Verifica si se encontró el elemento
if script_element:
    # Obtiene el contenido del script
    json_content = script_element.string

    # Parsea el contenido como JSON
    try:
        json_data = json.loads(json_content)
        print(json_data)
    except json.JSONDecodeError as e:
        print(f"Error al analizar el JSON: {e}")
else:
    print("No se encontró el elemento con el selector especificado.")
