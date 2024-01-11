import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sentence_transformers import SentenceTransformer, util
from webdriver_manager.chrome import ChromeDriverManager

innitUrl = "https://www.linkedin.com/jobs/search/?alertAction=viewjobs&currentJobId=3742697011&f_TPR=r86400&f_WT=2&geoId=101174742&location=Canada&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true&start="
pages = 50
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def load_file_to_array(file_path):
    data_array = []
    with open(file_path, 'r') as file:
        for line in file:
            data_array.append(line.strip())
    return data_array


def check_strings_in_array(string_array, target_string):
    for element in string_array:
        if element.lower() in target_string.lower():
            return True
    return False


def embed_titles(titles_array):
    ret = []
    for title in titles_array:
        ret.append(model.encode(title, convert_to_tensor=True))
    return ret


lines_array = load_file_to_array('job_titles.txt')
titles_array = load_file_to_array('ignore_titles.txt')
companies_array = load_file_to_array('ignore_companies.txt')
titles_embedding = embed_titles(titles_array)

# ------------------------------------------

chrome_options = Options()

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
url = "https://www.linkedin.com"
driver.get(url)
time.sleep(20)  # Adjust this time as needed

try:
    for i in range(0, pages, 1):
        if i == 0:
            url = innitUrl + "true"
        else:
            num = i * 25
            url = url = innitUrl + str(num)

        driver.get(url)
        time.sleep(5)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        ul_element = soup.find('ul', class_='scaffold-layout__list-container')

        if ul_element:
            li_elements = ul_element.find_all('li', class_='jobs-search-results__list-item')

            for li in li_elements:
                # Find the <a> tag with class "job-card-container__link" for the job name and URL
                title_link = li.find('a', class_='job-card-container__link')

                # Find the <span> tag with class "job-card-container__primary-description" for the company name
                company_span = li.find('span', class_='job-card-container__primary-description')

                # Find the <li> tag with class "job-card-container__metadata-item" for additional information
                metadata_li = li.find('li', class_='job-card-container__metadata-item')

                if title_link and company_span:
                    job_name = title_link.get_text(strip=True)
                    company_name = company_span.get_text(strip=True)

                    # Extract the URL from the href attribute
                    job_url = title_link['href']

                    # Extract the URL from the href attribute
                    additional_info = metadata_li.get_text(strip=True)

                    if check_strings_in_array(titles_array, job_name):
                        pass
                    elif check_strings_in_array(companies_array, company_name):
                        pass
                    elif not "remote" in additional_info.lower():  # can be commented out or changed
                        pass  # can be commented out or changed
                    else:
                        embedding_1 = model.encode(job_name, convert_to_tensor=True)
                        for embedding_2 in titles_embedding:
                            distance = util.pytorch_cos_sim(embedding_1, embedding_2)
                            tensor_value = distance.item()
                            if (tensor_value > 0.4):
                                print(f"https://www.linkedin.com{job_url}")
                                # print(f"Job Name: {job_name}")
                                # print(f"Company Name: {company_name}")
                                # print(f"Job URL: {job_url}")
                                # print(f"Additional Info: {additional_info}")
                                # print("------")
                                break

except:
    pass
