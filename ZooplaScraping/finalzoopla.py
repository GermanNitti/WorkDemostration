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
        
        # Crear una lista para almacenar las URLs
        url_list = []
        
        # Iterar sobre los elementos encontrados
        for link in url_links:
            # Obtener el valor del atributo href de cada elemento y agregarlo a la lista
            href_valor = link.get('href')
            url_list.append(href_valor)
            

        # Iterar sobre las URLs y acceder a cada una para extraer más URLs dentro de ellas
        for url in url_list:
            print("Accediendo a la URL:", url)
            driver.get(url)
            time.sleep(5)
              # Espera para que se cargue el contenido de la nueva página
            
            # Obtener el HTML de la página cargada
            html = driver.page_source
            
            # Crear un objeto BeautifulSoup para analizar el HTML de la nueva página
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encuentra los elementos con el selector específico dentro de la nueva página
            divs = soup.find_all('div', class_='clearfix bottom')  # Cambia 'tu_clase_div' por la clase real de tu div
            for div in divs:
                uls = div.find_all('ul', class_='bullet-col-3-alpha')  # Cambia 'tu_clase_ul' por la clase real de tu ul
                for ul in uls:
                    lis = ul.find_all('li')
                    for li in lis:
                        links = li.find_all('a', href=True)
                        for link in links:
                            # Obtener el valor del atributo href de cada elemento y hacer alguna operación
                            other_href = link.get('href')
                            print("Otra URL encontrada:", other_href)
                            # Realizar alguna operación adicional con la otra URL
                            # Tu código aquí...

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()

# Uso del ejemplo
url_to_scrape = "https://www.zoopla.co.uk/find-agents/estate-agents/"
fetch_data(url_to_scrape)
