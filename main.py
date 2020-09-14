import requests
from bs4 import BeautifulSoup
import json, glob
import pandas as pd
import time

def check_url_status():

    print('Check URL Status')

    urls = 'https://racecarsdirect.com/Category/Details/9/race-cars?page=1'

    res = requests.get(urls, headers={'User-Agent': 'Mozilla/5.0'})

    print(res.status_code)

    print('Checking status complete!')

    soup = BeautifulSoup(res.text, 'html.parser')

    total_page = soup.find('li', class_='PagedList-skipToLast').find('a')['href']
    total_page = total_page.split('=')

    total_page = total_page[1]

    return total_page

def get_urls_all_item(page):
    print(f'Getting all urls... page{page}')

    params = {
        'page': page
    }

    res = requests.get('https://racecarsdirect.com/Category/Details/9/race-cars', params=params, headers={'User-Agent': 'Mozilla/5.0'})

    soup = BeautifulSoup(res.text, 'html.parser')

    titles  = soup.find_all('div', class_='details')

    urls = []

    for title in titles:
        url = title.find('h3').find('a')['href']
        url = 'https://racecarsdirect.com' + url
        print(url)
        urls.append(url)

    return urls

def get_detail(url):

    print(f'Getting detail... {url}')

    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    soup = BeautifulSoup(res.text, 'html.parser')

    category = soup.find('ol', class_='breadcrumb')

    subcategory = category.find_all('li')
    subcategory = subcategory[-1].text

    title = soup.find('h1', class_='fancy').text.strip()

    image_url = soup.find('div', class_='item active').find('img')['src']
    image_url = 'https://racecarsdirect.com' + image_url

    descriptions = soup.find('div', class_='description translate').find_all('p')
    description = ''
    for desc in descriptions:
        description = description + desc.text

    table = soup.find('table', class_='table')
    header = table.find_all('th')
    for th in header:
        if th.text == 'Phone:':
            phone_number = th.next_sibling.next_sibling.get_text("|", strip=True)
        elif th.text == 'Currency:':
            currency = th.next_sibling.next_sibling.text.strip()
        elif th.text == 'Price:':
            price = th.next_sibling.next_sibling.text.strip()

    dict_data = {
        'title': title,
        'subcategory': subcategory,
        'image_url': image_url,
        'description': description,
        'phone_number': phone_number,
        'currency': currency,
        'price': price
    }

    with open(f'./results/{url.replace("/","")}.json', 'w') as outfile:
        json.dump(dict_data, outfile)

def create_excel():

    files = sorted(glob.glob('./results/*.json'))

    datas = []
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            datas.append(data)

    df = pd.DataFrame(datas)
    df.to_excel('result.xlsx')

    print('Excel ready...')

def run():

    while True:
        options = int(input('Number: '))

        if options == 1:
            total_page = check_url_status()

        if options == 2:
            total_urls = []
            for i in range(int(total_page)):
                page = i + 1
                urls = get_urls_all_item(page)
                total_urls += urls
                time.sleep(2)

            with open('all_urls.json', 'w') as outfile:
                json.dump(total_urls, outfile)

        if options == 3:

            with open('all_urls.json') as json_file:
                all_url = json.load(json_file)

            for url in all_url:
                try:
                    get_detail(url)
                    time.sleep(3)
                except:
                    pass

        if options == 4:
            create_excel()

        if options == 9:
            break


if __name__ == '__main__':
    run()

    # https://racecarsdirect.com/Advert/Details/107153/cooper-t59-fj-2662-formula-junior <- last
