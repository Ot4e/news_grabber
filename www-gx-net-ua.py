import re
import requests
import json
from bs4 import BeautifulSoup


seed = "https://gx.net.ua/"


def get_page_content(link):
    """Извлекаем даные с новостной страницы"""
    
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    page_info = {
        "url": link,  # ссылка на новость
        "title": "",  # заголовок новости
        "img": "",  # ссылка на изображение
        "body": "",  # текст новости
        "author": "",  # автор новости (если указывается)
        "date": "",  # дата публикации новости в формате YYYY-MM-DD
        "time": "",  # время публикации новости в формате HH:MM
    }
    

    page_info["title"] = soup.find("h1", class_="post-title").text.strip()
    
    page_info["author"] = soup.find('div', itemprop="author").text.strip()
    
    time_data=soup.find('time', itemprop="datePublished")
    
    page_info["time"] = time_data.text[-5:]
    
    page_info["date"] = time_data.attrs['datetime']
    
    page_info["img"] = soup.find('img', class_="attachment-highlight-block wp-post-image").attrs['src']
    
    # извлекаем текст статьи и убираем рекламный блок
    div = soup.find('div', itemprop="articleBody")
    #находимм начало рекламного блока
    start_substr = div.text.find('Читайте также:')
    #находим конец рекламного блока
    end_substr = div.text[start_substr:].find('\n')
    
    article = div.text[:start_substr] + div.text[start_substr+end_substr:]
    
    #избавляемся от рекламной подписи
    article = article.replace('\nПодписывайтесь на наш Teleram-канал:\xa0https://t.me/gx_net_ua\n', '')

    #избавляемся от лишних символов перевода строки
    while len(re.findall('\\n{2}', article)) > 0:
        article = re.sub('\\n{2}', '\\n', article)
    
    page_info["body"] = article
    
    return page_info


def get_links():
    """Получаем список ссылок на новости с главной страницы"""

    try:
        r = requests.get(seed)
        soup = BeautifulSoup(r.content, "html.parser")
        ref = soup.find_all('div', class_="read-more visible-sm2")
        links = []
        for items in ref[5:]:
           links.append(seed + items.a['href'][1:])
        
        return links

    except requests.exceptions.ConnectionError:
        print(f'Не удалось выполнить соединение с {seed}')
        return []


def main():
    """Данные по каждой новостной странице записываем в файл"""

    links = get_links()
    top_news = []
    for link in links:
        print(f"Обрабатывается {link}")
        info = get_page_content(link)
        top_news.append(info)

    with open("www-news-com.json", "wt") as f:
        json.dump(top_news, f,)
    print("Работа завершена")
    

# Главная функция
if __name__ == "__main__":
    main()
    
     