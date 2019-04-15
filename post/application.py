import requests
import re
import json
import datetime
from pushbullet import Pushbullet

def get_prices_from_book(book):
    r = requests.get(book['url'])

    regex_tag = re.compile("m-min.*/strong")
    tag_matches = regex_tag.findall(r.text)

    regex_price = re.compile(r"\d+,\d+")
    prices = []

    for tag_match in tag_matches:
        price_match = regex_price.findall(tag_match)
        if len(price_match) != 1:
            raise "Formato do DOM foi alterado! Checar 'm-min'."
        #Substituindo vírgulas por pontos pois é assim que o resto do mundo escreve decimais
        price = float(price_match[0].replace(',', '.'))
        prices.append(price)
    
    return prices

def get_books_from_file(filename):
    file_content = open(filename, 'r', encoding = 'utf-8')
    return json.load(file_content)

def save_books_to_file(filename, books):
    file_content = open(filename, 'w', encoding = 'utf-8')
    json.dump(books, file_content, indent = 2, ensure_ascii=False)

def get_notification_from_updated_books(book_updates):
    title = "Novos livros na Estante Virtual!"
    body = ""
    for book_update in book_updates:
        body += book_update['name']
        prices = sorted(book_update['new_prices'])
        for price in prices:
            body += "\n\t\t\t* "
            body += "R$ {:,.2f}".format(price).replace(".", ",")
        if book_updates.index(book_update) < len(book_updates) - 1:
            body += "\n"
    return title, body

def notify_phone(title, body):
    API_KEY = 'o.WQBE18NFPg6v2k2kB8BD4eo1MrXLzYIc'
    pb = Pushbullet(API_KEY)
    pb.push_note(title, body)

def get_unique_items(my_list):
    return list(set(my_list))

filename = 'livros.json'

try:
    books = get_books_from_file(filename)
    updated_books = []

    for book in books:
        current_prices = get_prices_from_book(book)
        new_prices = []

        for current_price in current_prices:
            if current_price not in book['prices'] and current_price not in new_prices:
                new_prices.append(current_price)
        
        # Não queremos armazenar valores repetidos
        book['prices'] = get_unique_items(current_prices)
        book['last_modified'] = str(datetime.datetime.now())

        if len(new_prices) != 0:
            updated_books.append({"name": book['name'], "new_prices": new_prices})

    save_books_to_file(filename, books)

    if len(updated_books) > 0:
        title, body = get_notification_from_updated_books(updated_books)
        notify_phone(title, body)
except Exception as err:
    notify_phone("Estante Virtual Crawler: Something went wrong!", err)