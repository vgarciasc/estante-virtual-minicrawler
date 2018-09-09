from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from oauth2client import file, client, tools
import base64
import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.send'

def create_message(sender, to, subject, message_text):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    part1 = MIMEText(message_text, 'plain')
    part2 = MIMEText(message_text, 'html', 'utf-8')

    message.attach(part1)
    message.attach(part2)

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    return {'raw': b64_string }

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
        print('Message Id: %s' % message['id'])
        return message
    except:
        print('An error occurred')

def notification(book_list):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    string = "Os seguintes livros receberam novos preços:<br>"
    for book in book_list:
        string += "<b><a href=\"" + 'https://www.estantevirtual.com.br/busca?q=' + book.search_str + "\">" + book.name + "</a></b>"
        string += "<br>"
        string += "<ul>"
        for price in book.new_prices:
            string += "<li>" + price + "</li>"
        string += "</ul>"
        string += "<br>"
        string += "<br>"

    subject = '\U0001F4D8 Estante Virtual Crawler - [' + str(datetime.datetime.now()) + ']'

    msg = create_message(SENDER, SENDER, subject , string)
    send_message(service, 'me', msg)