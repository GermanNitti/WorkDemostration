import requests
from bs4 import BeautifulSoup
import re
import csv
import concurrent.futures

class WebScraper:
    """
    A class to scrape data from web pages.
    """
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

    def get_page_content(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page: {e}")
            return None

    def extract_job_details(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        selectors = {
            'Recruiter': '.job-detail-description__recruiter dd',
            'Location': '.job-detail-description__location dd',
            'Salary': '.job-detail-description__salary dd',
            'Posted': '.job-detail-description__posted-date dd',
            'Closes': '.job-detail-description__end-date dd',
            'Ref': '.job-detail-description__job-ref dd',
            'Contact': '.job-detail-description__contact-name dd',
            'Job Title': '.job-detail-description__category-StaticJobTitle dd',
            'Practice Area': '.job-detail-description__category-PracticeArea dd',
            'PQE Level': '.job-detail-description__category-PQELevel dd',
            'Contract Type': '.job-detail-description__category-ContractType dd',
            'Hours': '.job-detail-description__category-Hours dd',
            'Description': '.job-description'
        }

        job_details = {}
        for key, selector in selectors.items():
            element = soup.select_one(selector)
            if key != "Description":
                job_details[key] = re.sub('\s+', ' ', element.text.replace('\n', '').strip()) if element else None
            else:
                job_details[key] = element.text if element else None
        return job_details

def get_job_listing_urls(base_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching the base page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    ul_list = soup.find('ul', class_='paginator__items no-margin float-right')
    if not ul_list:
        return []

    last_list_item = ul_list.find_all('li')[-1]
    a_element = last_list_item.find('a')
    if not a_element:
        return []

    href_value = a_element.get('href')
    num_pages = int(re.search(r'\d+', href_value).group())
    # num_pages=5

    job_urls = []
    for page_number in range(1, num_pages + 1):
        print("Accessing page",page_number)
        page_url = f"{base_url}{page_number}"
        page_response = requests.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        job_links = page_soup.select('.lister__details a[href]')
        job_urls.extend(["https://totallylegal.com" + link["href"].strip() for link in job_links])

    return job_urls

def scrape_job_data(job_url):
    scraper = WebScraper(job_url)
    page_content = scraper.get_page_content()
    if page_content:
        job_details = scraper.extract_job_details(page_content)
        print(f"Extracted data from {job_url}")
        return job_details
    else:
        return None

def scrape_and_save_jobs_to_csv_concurrently(job_urls, csv_file_name):
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Recruiter', 'Location', 'Salary', 'Posted', 'Closes', 'Ref',
                      'Contact', 'Job Title', 'Practice Area', 'PQE Level', 'Contract Type', 'Hours', 'Description']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(scrape_job_data, url): url for url in job_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                job_details = future.result()
                if job_details:
                    csv_writer.writerow(job_details)
                    csv_file.flush()

        print(f"All data has been saved to the CSV file: {csv_file_name}")

# Main execution
base_url = "https://www.totallylegal.com/jobs/"
job_listing_urls = get_job_listing_urls(base_url)
scrape_and_save_jobs_to_csv_concurrently(job_listing_urls, 'extracted_job_data.csv')
