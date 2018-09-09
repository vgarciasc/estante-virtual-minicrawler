#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import hashlib
import datetime
import json
from win10toast import ToastNotifier

filename_data = 'estante_virtual_data.json'
filename_notification_books = 'estante_virtual_novos.json'

class Book:
    def __init__(self, name, search_str, matches, new_prices, last_modified):
        self.name = name
        self.search_str = search_str
        self.matches = matches
        self.new_prices = new_prices
        self.last_modified = last_modified

books = json.load(open(filename_data, 'r'))
books_serializable = []
notification_books = []

for book in books:
    book = Book(book['name'], book['search_str'], book['matches'], book['new_prices'], book['last_modified'])

    search_url = 'https://www.estantevirtual.com.br/busca?q=' + book.name

    r = requests.get(search_url)

    regex = re.compile("busca-price-fromto.*?strong")
    matches = regex.findall(str(r.content))

    #retirar preços repetidos
    matches = list(set(matches))

    new_prices = []
    for match in matches:
        if match not in book.matches:
            new_prices.append(match)

    if matches == []:
        book.matches = matches

    if len(new_prices) > 0:
        #alteracao nos preços
        book.matches = matches
        book.last_modified = str(datetime.datetime.now())
        notification_books.append(book.name)

    book.new_prices = new_prices

    books_serializable.append(book.__dict__)

json.dump(books_serializable, open(filename_data, 'w', encoding = 'utf-8'), indent = 2, ensure_ascii=False)

if len(notification_books) > 0:
    toaster = ToastNotifier()
    toaster.show_toast("Novos Preços: Estante Virtual", str(notification_books))

json.dump(notification_books, open(filename_notification_books, 'w', encoding = 'utf-8'), indent = 2, ensure_ascii=False)