
import json, time, random
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import cloudscraper
from datetime import datetime
import os
import uuid
import concurrent.futures
import csv


# Function named new_scraper that returns a cloudscraper object with specific configurations

# Define the function
def new_scraper():

    l=[{
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    },
    {
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    },
    {
        'browser': 'firefox',
        'platform': 'android',
        'mobile': True
    },
    {
        'browser': 'chrome',
        'platform': 'ios',
        'mobile': True
    },
    {
        'browser': 'chrome',
        'platform': 'darwin',
        'mobile': False
    },
    {
        'browser': 'firefox',
        'platform': 'darwin',
        'mobile': False
    }
    ]
    # session = requests.session()

    # sess=requests.Session()
    return cloudscraper.create_scraper(disableCloudflareV1=random.choice([True, False]), interpreter='v8', browser=random.choice(l))
   
    # return cloudscraper.create_scraper(disableCloudflareV1=True, interpreter='v8', browser={
    #     'browser': 'chrome',
    #     'platform': 'windows',
    #     'mobile': False
    # })



def get_product_urls(sitemap):
    products=[]
    scraper=new_scraper()
    response=scraper.get(sitemap)
    
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        sitemaps = soup.find_all('loc')
        for smp in [sitemaps[4]]:
            print("Sitemap",smp.text)
            response_sm = scraper.get(smp.text)
            print(response_sm.status_code)
            if response_sm.status_code == 200:
                sm_soup = BeautifulSoup(response_sm.text, 'xml')
                found_products = sm_soup.find_all('loc')
                for product in found_products:
                    path=urlparse(product.text).path
                    if not path.startswith('/search') and not path.count('/') >= 2 and path != '':
                        products.append(product.text)
    return products

def get_image(url,unique_dir):
    print("Getting image",url)
    try:
        scraper=new_scraper()
        response = scraper.get(url)
        print("image status",response.status_code)
        if response.status_code == 200:
            file_path = os.path.join(unique_dir, url.split('/')[-1].split("?")[0])
            with open(file_path, 'wb') as file:
                file.write(response.content)
    except Exception as e:
        print(e)
        time.sleep(10)
        get_image(url,unique_dir)

def scrape_product(url,tries):
    
    scraper=new_scraper()
    print(url)
    try:
        req=scraper.get(url)

        print("pdp status",req.status_code)
        if req.status_code==403:
            if tries<5:
                time.sleep(120)
                return scrape_product(url,tries+1)
        soup = BeautifulSoup(req.content.decode(), 'html.parser')

        # In this element lies all the information in json format
        j = soup.select('#__NEXT_DATA__')
        data=json.loads(j[0].text)
        data_object={}
        # Find the right key on the json data, this is a list so we need to go one by one until we find the right one
        for query in data["props"]["pageProps"]["req"]["appContext"]["states"]["query"]["value"]["queries"]:
            if "GetProduct" in query["queryHash"]:
                data_object=query["state"]["data"]["product"]
                break

        product_title=data_object["primaryTitle"]
        brand=data_object["brand"]

        release_date=""
        colorway=""
        retail_price=0
        sku=""
        image_url_list=data_object["media"]["all360Images"]
        gallery=data_object["media"]["gallery"]
        image_url_list=image_url_list+gallery

        print(image_url_list)



        parent_dir = 'images/'
        dir_name=str(uuid.uuid4())

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        unique_dir = os.path.join(parent_dir, dir_name)
        if not os.path.exists(unique_dir):
            os.makedirs(unique_dir)

        for url_image in image_url_list:
            get_image(url_image,unique_dir)



        for trait in data_object["traits"]:
            if trait["name"]=="Release Date":
                release_date=trait["value"]
            if trait["name"]=="Colorway":
                colorway=trait["value"]
            if trait["name"]=="Retail Price":
                retail_price=trait["value"]
            if trait["name"]=="Style":
                sku=trait["value"]

        print(datetime.now())

        return {
            "url":url,
            "title":product_title,
            "releaseDate":release_date,
            "retailPrice":retail_price,
            "sku":sku,
            "brand":brand,
            "colorway":colorway,
            "releaseDate":release_date,
            "imagesFolder":dir_name
        }
    except Exception as e:
        print(e)
        if tries<5:
            time.sleep(120)
            # scraper=new_scraper()

            return scrape_product(url,tries+1)
        else:
            return {}
        


# full_products=get_product_urls("https://stockx.com/sitemap/sitemap-index.xml")
# for prod in full_products:
#     print("======",prod)
#     result=scrape_product(prod,0)
#     print(result)




def append_to_csv(data, filename):
    keys = data.keys()
    with open(filename, 'a', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writerow(data)

def main():
    full_products = get_product_urls("https://stockx.com/sitemap/sitemap-index.xml")

    # Create the CSV file and write the header
    with open('scraped_data.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        # Assuming the first product will have all keys. Adjust as necessary.
        if full_products:
            sample_product = scrape_product(full_products[0], 0)
            writer.writerow(sample_product.keys())

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scrape_product, prod, 0): prod for prod in full_products}
        for future in concurrent.futures.as_completed(futures):
            prod = futures[future]
            try:
                result = future.result()
                print(f"Result for {prod}: {result}")
                append_to_csv(result, 'scraped_data.csv')
            except Exception as exc:
                print(f"Error for {prod}: {exc}")

if __name__ == "__main__":
    main()


# print(scrape_product("https://stockx.com/awake-subway-series-mets-t-shirt-royal",0)) 
 

