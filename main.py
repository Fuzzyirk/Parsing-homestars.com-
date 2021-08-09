import requests
from bs4 import BeautifulSoup
import time
import json
import random
import os


def find_category_links(url, head):
    category_links = {}
    response = requests.get(url, headers=head)
    print('статус подключения - ', response.status_code)
    text = response.text
    soup = BeautifulSoup(text, "lxml")
    lis = soup.find_all(class_='category-group__list-item')
    for li in lis:
        href = li.find(class_="category-group__link").get("href")
        category_links[href.split("/")[3]] = 'https://homestars.com' + href
    print('Количество котегорий - ', len(category_links))
    for k, v in category_links.items():
        print(k, ' - ', v)
    return category_links


def find_company_links(category_links):
    company_links = []
    company_links_and_companies = {}
    for category_name, category_link in category_links.items():
        print(f'Компаний в категории {category_name} - ', how_many_companies(category_link))
        print(how_many_companies(category_link) // 10 + 2)
        for i in range(1, how_many_companies(category_link) // 10 + 2):
            link = category_link + f'?page={i}'
            print(link)
            try:
                response = requests.get(link, headers=header)
            except Exception as err:
                print('Не получается подключиться к странице списка компаний', err)
                break
            try:
                soup = BeautifulSoup(response.text, "lxml")
                divs = soup.find_all('script', attrs={"type": "application/ld+json"})
                for div in divs:
                    js = json.loads(div.string)
                    print(js["@id"])
                    company_links.append(js["@id"])
            except Exception as err:
                print('Не получается распарсить страницу списка компаний', err)
            time.sleep(random.randint(1, 3))
        print('Найденные ссылки на компании - ', len(company_links))
        print('Ссылок без дубликатов - ', len(set(company_links)))
        company_links_and_companies[category_name] = set(company_links)
        print('----------------------------------------------------------------------------------------------------')
    return company_links_and_companies


def find_company_info(company_links_and_companies):
    for category_name, company_links in company_links_and_companies.items():
        for company_link in company_links:
            try:
                response = requests.get(company_link, headers=header)
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as err:
                print('Ошибка парсинга страницы компании', err)
                break
            try:
                name = soup.find('div', class_="company-header-details").find('h1').text
            except Exception as err:
                print('Не найдено имя компании по ссылке', err)
                name = 'Unknown'
            if name == 'Unknown':
                try:
                    name = soup.find('a', class_="free-company-header-details__name").find('h1').text
                except Exception as err:
                    print('Не найдено имя компании по ссылке', err)
                    name = 'Unknown'
            try:
                webadr = soup.find('a', class_="company-listing-subnav-contact__button").get('href')
            except Exception as err:
                print('Не найдена ссылка компании', err)
                webadr = 'Unknown'
            try:
                phone = soup.find('div', class_="company-listing-subnav__contact-buttons").find('span').text
            except Exception as err:
                print('Не найден телефон компании', err)
                phone = 'Unknown'
            csv_writer(category_name, name, webadr, phone, company_link)
            time.sleep(random.randint(1, 4))


def csv_writer(category, name, link, phone, homestars_link):
    if not os.path.exists('csv'):
        os.mkdir('csv')
    try:
        row = name + ';' + link + ';' + phone + ';' + homestars_link + "\n"
        print('Записываю строку в csv - ', row)
        with open(f"csv\{category}.csv", 'a', encoding='utf-8') as file:
            file.write(row)
    except Exception as err:
        print(err)


def how_many_companies(link):
    try:
        response = requests.get(link, headers=header)
        soup = BeautifulSoup(response.text, "lxml")
        divs = soup.find('div', attrs={"data-react-class": "SearchResultsNav"})
        pages_str = str(divs).split("totalHits")[1]
        hits = int(''.join(filter(str.isdigit, pages_str)))
        return hits
    except Exception as err:
        print('Ошибка поиска количества компаний!', err)
        return 667


if __name__ == '__main__':
    URL = 'https://homestars.com/on/toronto/categories'
    header = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.107 "
                      "Safari/537.36"
    }
    find_company_info(find_company_links(find_category_links(URL, header)))
