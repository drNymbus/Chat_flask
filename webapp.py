import time
from flask import *
import sys
import psycopg2

time_now = time.strftime("%H/%M/%S")

#NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)

def page(pseudo):
    page = """<html>
    <head>
      <title>Cool Chat :)</title>
      <style>
       .pseudo {
          float:right;
          width:30%;
          height:80%;
    	  overflow-y: auto;
        }
        .message {
          float:left;
          width:70%;
          height:80%;
    	  overflow-y: auto;
        }
      </style>
    </head>
    <body background="background.jpg">"""
    page = page + "<div class=\"pseudo\">" + display_all_pseudo() + "</div>"
    page = page + "<div class=\"message\">" + display_all_message() + "</div>"
    page = page + "<div class=\"message\">" + create_form(pseudo) + "</div>"
    page = page + "</body> </html>"
    return page

def create_form(pseudo):
    form = """<form method=\"POST\" action=\"chat\">
      <input type=\"text\" name=\"message\" placeholder=\"Enter message here\" />
      <input type=\"submit\" value=\"Submit\" />
      <input type=\"hidden\" name=\"pseudo\" value=\"""" + pseudo + """\" />
      <input type=\"submit\" value=\"Refresh\" onClick=\"window.location.reload()\">
    </form>"""
    return form

@app.route("/")
def insert_id():
    return app.send_static_file("form.html")


@app.route("/log_in", methods=['POST'])
def enter_login():
    pseudo_session = request.form['pseudo']
    print(pseudo_session)
    print('available ? ' + str(pseudo_available(pseudo_session)))
    if pseudo_available(pseudo_session):
        enter_pseudo(pseudo_session)
        return page(pseudo_session)
    return app.send_static_file("form_reEnter_pseudo.html")

@app.route("/chat", methods=['POST'])
def chat():
    pseudo = request.form['pseudo']
    message = request.form['message']
    if message == '/tuveuxvraimentoutsupprimer':
        suppress_all()
        return page(pseudo)
    if message == '':
        return page(pseudo)
    if message == '/offline' or message == '/off':
        return suppress_session(pseudo)
    else:
        enter_message(pseudo, message)
    return page(pseudo)

def enter_pseudo(pseudo):#permet d'inserer un pseudo dans la bd
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        enter_pseudo = 'insert into MonChat.Pseudo values (\'' + pseudo + '\');'
        try:
            cur.execute(enter_pseudo)
            conn.commit()
            return enter_message('Bot', 'Say \"Hi!\" to your new friend, the magnificient: ' + pseudo)
        except Exception as e :
            return 'Problem on: ' + str(e)
    except Exception as e :
        return "Cannot connect to database" + str(e)

def enter_message(pseudo, message):#permet d'inserer un message dans la bd
    hour = time.strftime("(%H:%M:%S)")
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        enter_message = "insert into MonChat.Message values (\'" + pseudo + "\', \'" + hour + "\', \'" + message + "\');"
        try:
            print(enter_message)
            cur.execute(enter_message)
            conn.commit()
            return
        except Exception as e :
            return 'No idea: ' + str(e)
    except Exception as e :
        return 'Cannot connect to database ' + str(e)

def pseudo_available(pseudo):#verifie que le pseudo rentrer n'est pas deja existant
    if pseudo.lower() == 'bot':
        return False
    else:
        try:
            conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
            cur = conn.cursor()
            check_pseudo = 'select Pseudonyme from MonChat.Pseudo;'
            try:
                cur.execute(check_pseudo)
                rows_pseudo = cur.fetchall()
                for row in rows_pseudo:
                    if pseudo == row[0]:
                        return False
                return True
            except Exception as e :
                return 'No idea : ' + str(e)
        except Exception as e :
            return "Cannot connect to database" + str(e)

def display_all_pseudo():#affiche les pseudos
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        display_pseudo = 'select Pseudonyme from MonChat.Pseudo;'
        try:
            cur.execute(display_pseudo)
            rows_pseudo = cur.fetchall()
            all_pseudo ='<h1>All users</h1> ------ <br>'
            for row in rows_pseudo:
                all_pseudo = all_pseudo + row[0] + '<br>'
            all_pseudo = all_pseudo + '</body>  '
            return all_pseudo
        except Exception as e :
            return 'No idea : ' + str(e)
    except Exception as e :
        return "Cannot connect to database " + str(e)


def display_all_message():#affiche les messages
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        take_mess = 'select * from MonChat.Message;'
        try:
            cur.execute(take_mess)
            rows_message = cur.fetchall()
            page_message = """<h1>
              Lobby (type /off to disconnect)
            </h1>
            <h2>
              (to display \' u need to type \\\') <br>
              (to refresh message just click the button Refresh) <br>
            </h2>
            <br>"""
            nb_total_messages = 0
            for i in rows_message:
                nb_total_messages+=1
            compteur = 0
            for row in rows_message:
                compteur+=1
                if nb_total_messages-compteur <= 100:
                    page_message = page_message + row[0] + ' ' + row[1]+ ': ' + row[2] + '<br>'
            return page_message
        except Exception as e:
            return 'No idea: ' + str(e)
    except Exception as e :
        return 'Cannot connect to database' + str(e)


def suppress_session(pseudo):#supprime un pseudo, ainsi que tout les messages envoyes, de la bd
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        suppress_pseudo = 'delete from MonChat.Pseudo where Pseudonyme = \'' + pseudo + '\';'
        suppress_message = 'delete from MonChat.Message where Pseudonyme = \'' + pseudo + '\';'
        try:
            cur.execute(suppress_message)
            conn.commit()
            cur.execute(suppress_pseudo)
            conn.commit()
            return 'You\'re disconnected from the chat. <br> See you later ;) <br>'
        except Exception as e :
            return 'No idea: ' + str(e)
    except Exception as e :
        return 'Cannot connect to database ' + str(e)

def suppress_all():#permet de reinitialiser totalement la bd
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        all_pseudos = 'select Pseudonyme from MonChat.Pseudo;'
        try:
            cur.execute(all_pseudos)
            rows_pseudos = cur.fetchall()
            for row in rows_pseudos:
                suppress_session(row[0])
            return
        except Exception as e :
            return 'No idea: ' + str(e)
    except Exception as e :
        return 'Cannot connect to database ' + str(e)

def try_conn():#je n'ai pas reussi a factoriser la connection au serveur
#l'erreur "object has no attribute 'execute' " m'en a empeche
    try:
        conn = psycopg2.connect("host=dbserver dbname=vmelancon user=vmelancon")
        cur = conn.cursor()
        return cur
    except Exception as e :
        return e

#NE SURTOUT PAS MODIFIER
if __name__ == "__main__":
   app.run(debug=True)
