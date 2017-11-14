import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()


TOKEN = "424323881:AAG1ZFSVti-959-oQCQH8Oadr-WxuM0qcaY"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def handle_updates(updates):
    for update in updates["result"]:
        text=None
        if "from" in update["message"]:
            chat = update["message"]["chat"]["id"]
            persona = update["message"]["from"]["username"]
        else:
            chat = update["message"]["chat"]["id"]
            persona = chat

        if "text" in update["message"]:
            text = update["message"]["text"]
        elif "new_chat_participant" in update["message"]:
            send_message("Hola a todo el mundo \xF0\x9F\x98\x89 ",chat)
        elif"sticker" in update["message"]:
            text = update["message"]["sticker"]["emoji"]


        items = db.get_items(chat)
        if(text):
            if text == "/chat" or text == "/chat@Herruzo_bot":
                a , b = items
                if  a:
                    messages= a[0]+": "+b[0]
                else:
                    messages = "No hay mensajes"
                for x in range(1, len(a)):
                    final=("{}: {}".format(a[x], b[x]))
                    messages=messages+"\n"+final
                send_message(messages,chat)
            elif text == "/borrar_chat"or text == "/borrar_chat@Herruzo_bot":
                db.delete_group(chat)
                send_message("Mensajes borrados",chat)
            elif text.startswith("/"):
                continue
            else:
                db.add_item(text,persona,chat)
                items = db.get_items(chat)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=HTML".format(text, chat_id)
    get_url(url)

def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
