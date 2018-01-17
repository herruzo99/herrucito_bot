import json
import requests
import time
import urllib
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from dbhelper import DBHelper

db = DBHelper()


TOKEN = "424323881:AAG1ZFSVti-959-oQCQH8Oadr-WxuM0qcaY"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    try:
        response = requests.get(url)
        content = response.content.decode("utf8")
    except:
        content = None;
        log=open('log.txt','w')
        log.write("rip telegram")
        send_message("Parece que se calle telegram","274428442")
        pass
    return content



def get_xml_from_url(url):
    response=requests.get(url)
    content = response.content.decode("utf8")
    return ET.fromstring(content)


def get_json_from_url(url):
    try:
        content = get_url(url)
        if content:
            js = json.loads(content)
        else:
            js = None;
    except:
        print("Error"+ content)
        js = None;
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

def handle_updates(updates,now):
    for update in updates["result"]:
        text=None
        try:
            if "from" in update["message"]:
                chat = update["message"]["chat"]["id"]
                persona = update["message"]["from"]["username"]
                personaid = update["message"]["from"]["id"]
                tipo = update["message"]["chat"]["type"]
            else:
                chat = update["message"]["chat"]["id"]
                persona = chat
                personaid= chat
                tipo = update["message"]["chat"]["type"]

            if "text" in update["message"]:
                text = update["message"]["text"]
            elif "new_chat_participant" in update["message"]:
                send_message("Hola a todo el mundo",chat)
            elif"sticker" in update["message"]:
                text = update["message"]["sticker"]["emoji"]

            if tipo=="group" or tipo=="supergroup":
                db.nuevo_chat(chat,1,None)
            elif tipo=="private":
                db.nuevo_chat(chat,0,None)

            if(text):

                if db.sacar_chat("calendario",chat)[0]==1:
                    a,b,c = db.get_all_eventos()
                    if text == "Todos":
                        message = proximos_eventos(now)
                    else:
                        aux = True
                        for x in range(0,len(c)):
                            if text == c[x]:
                                message = proximos_eventos(now,c[x])
                                aux = False
                        if aux:
                            message="Ese calendario no existe"
                    db.chat_calendario(0,chat)
                    send_message(message,chat)

                elif text == "/chat" or text == "/chat@Herruzo_bot":
                    items = db.get_items(chat)
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

                elif text == "/eventos"or text == "/eventos@Herruzo_bot":
                    db.chat_calendario(1,chat)
                    message="Que calendario quieres:\n-Todos\n"
                    a,b,c = db.get_all_eventos()
                    usados = ""
                    for x in range(0,len(c)):
                        if c[x] not in usados:
                            usados += c[x]
                            message = message + "-{}\n".format(c[x])
                    send_message(message,chat)

                elif text == "/calendario"or text == "/calendario@Herruzo_bot":
                        url="https://calendar.google.com/calendar"
                        message="Para editar el calendario asegurate de que tienes seleccionado el calendario del bot\n"+url+"\nAñade una nota al evento que sea:\n-Cumpleaños\n-Examen\n(Los eventos tienen que ser de <b>Todo el dia</b>)"
                        send_message(message,chat)

                elif text.startswith("/"):
                    continue

                else:
                    db.add_item(text,persona,personaid,chat)
                    while db.number_rows(chat)[0]>100:
                        db.auto_delete(chat)
        except KeyError:
            continue

def proximos_eventos(now,tipo=None):
    if tipo:
        recordatorios = db.get_eventos(tipo)
        a,b=recordatorios
    else:
        recordatorios = db.get_all_eventos()
        a,b,c=recordatorios
        tipo= "eventos"
    now = datetime.today() - timedelta(days=1)

    mensagge="Los próximos {} son:\n".format(tipo)
    for x in range(0,len(a)):
        if (datetime.strptime(b[x],"%Y-%m-%d %H:%M:%S")-now).days == 0:
            final=("<b>{}</b> hoy!\n").format(a[x])
        else:
            final=("<b>{}</b> en {} dias\n").format(a[x],(datetime.strptime(b[x],"%Y-%m-%d %H:%M:%S")-now).days)
        mensagge=mensagge+final
    return mensagge

def load_eventos(now):
    url="https://www.googleapis.com/calendar/v3/calendars/herruzobot@gmail.com/events?key=AIzaSyApeOPir0ZK7XzPEvQvgbbikZE5M2cl_Qk&orderBy=starttime&singleEvents=true"
    updates=get_json_from_url(url)
    db.limpiar_eventos()
    for update in updates["items"]:
        recordatorio=update["summary"]
        aux=update["start"]["date"]
        try:
            nota=update["description"]
        except:
            nota="Falta Nota"
        fecha=datetime.strptime(aux,"%Y-%m-%d")
        now = datetime.today() - timedelta(days=1)
        if (fecha-now).days >= 0 and (fecha-now).days < 365:
            db.nuevos_eventos(recordatorio,fecha,nota.replace("\n", ""))

def forecast_1():
    url="http://api.tiempo.com/index.php?api_lang=es&localidad=7652&affiliate_id=vw7ihuf35z2s&v=2"
    updates = get_xml_from_url(url)
    minima= updates[0][1][1].get("value")+updates[0][1][1].get("unit")
    maxima= updates[0][1][2].get("value")+updates[0][1][2].get("unit")
    frase= updates[0][1][0].get("desc")
    lluvia= updates[0][1][5].get("value")+updates[0][1][5].get("unit")
    return (frase,minima,maxima,lluvia)



def morning_update():
    fgrupos="0"
    grupos = db.get_grupos()
    tiempo = forecast_1()
    for x in range(0,len(grupos)):
        if x==0 or grupos[x] not in fgrupos:
            fgrupos+=grupos[x]
            send_document("CgADBAADFYMAArQdZAeoc4qGL83epwI",grupos[x])
            send_message("Buenos dias, hoy: {}, con una minima de {} y una maxima de {}, por último caerán {} de lluvia. Disfrutad del dia 😉".format(tiempo[0],tiempo[1],tiempo[2],tiempo[3]),grupos[x])


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=HTML".format(text, chat_id)
    get_url(url)

def send_document(doc, chat_id, reply_markup=None):
    url = URL + "sendDocument?document={}&chat_id={}".format(doc, chat_id)
    get_url(url)

def mute(grupo,persona,tiempo=None):
    if tiempo:
        times=int(time.time())+tiempo
        url=URL+"restrictChatMember?chat_id={}&user_id={}&can_send_messages=false&until_date={}".format(grupo,persona,times)
    else:
        url=URL+"restrictChatMember?chat_id={}&user_id={}&can_send_messages=false".format(grupo,persona)
    get_url(url)

def time_clauses(now,dia):
    if now.hour==6 and 29 < now.minute < 31 and dia:
        morning_update()
        dia = False
    elif now.minute > 31:
        dia = True
    if now.hour==0 and 29 < now.minute < 31:
        load_eventos(now)

def main():
    dia = True
    db.setup()
    last_update_id = None
    send_message("Activo","274428442")

    while True:
        try:
            now = datetime.now()+timedelta(hours=1)
            time_clauses(now,dia)
            load_eventos(now)
            print (now.year, now.month, now.day, now.hour, now.minute, now.second)
            updates = get_updates(last_update_id)
            if updates:
                if len(updates["result"]) > 0 and updates:
                    last_update_id = get_last_update_id(updates) + 1
                    handle_updates(updates,now)
            else:
                time.sleep(100)
        except KeyError as e:
            log=open('log.txt','w')
            log.write(e)
            send_message("cai bien","274428442")
        except:
            log=open('log.txt','w')
            log.write("otro fallo")
            send_message("cai mal","274428442")


if __name__ == '__main__':
    main()
