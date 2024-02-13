from undetected_chromedriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup
import time




def fetch_data(url, output_file="ZooplaOutput.txt"):
    driver_path = '/home/german/Documentos/Work'
    options = ChromeOptions()
    driver = Chrome(executable_path=driver_path, options=options)

    
    try:
        driver.get(url)
        time.sleep(5)  # Espera para que se cargue el contenido
        
        # Obtener el HTML de la página cargada
        html = driver.page_source
        
        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encuentra los elementos 'a' con los atributos especificados
        url_links = soup.findAll('a', {'style': 'padding-left: 0;', 'class': 'btn-browse-row-clickable', 'href': True})
        
        # Crear una lista para almacenar los valores de href
        href_valores = []

        # Iterar sobre los elementos encontrados
        for link in url_links:
            # Obtener el valor del atributo href de cada elemento y agregarlo a la lista
            href_valor = link.get('href')
            href_valores.append(href_valor)

        # Imprimir los valores de href separados por líneas
        for href_valor in href_valores:
            print(href_valor)

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()

# Uso del ejemplo
url_to_scrape = "https://www.zoopla.co.uk/find-agents/estate-agents/"
fetch_data(url_to_scrape)