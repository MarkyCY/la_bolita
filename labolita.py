from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
from telebot.types import ReplyKeyboardRemove
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import telebot
import json
import pytz
import re
import threading
import requests
import charada2 as charada_srch

# Cargando las variables de entorno desde el archivo .env
load_dotenv()

# Accediendo a la variable global
telebot_token = os.getenv('TELEBOT')

# Inicialización del bot de Telegram
bot = telebot.TeleBot(telebot_token)

# Almacenar la hora actual y convertirla a formato militar (sin AM/PM)
now = datetime.now()
military_time = int(now.strftime("%H"))

# Declarar variables globales vacías
usuarios = {}
game = {}

# Conectarse a la base de datos MongoDB y crear las colecciones "users" y "juegos"
client = MongoClient('localhost', 27017)
db = client.bolita
users = db.users
juegos = db.juegos
charada = db.charada

tdb = db = client.test
test = db.juegos

# Función para convertir una cadena en una lista de caracteres
def Convert(string):
    li = list(string)
    return li

# Función para convertir una lista de caracteres en una cadena
def listToString(s):
    str1 = ""
    return (str1.join(s))

# Función para verificar si una cadena tiene el formato "numero-numero"
def verificar_formato(cadena):
    # Dividir la cadena por el carácter "-"
    elementos = cadena.split("-")
    # Verificar si hay dos elementos y si son números
    return len(elementos) == 2 and elementos[0].isdigit() and elementos[1].isdigit()

#BOT MAIN ***********************************************************************



# Define la estructura de los botones de inicio
botones_home = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=5)
botones_home.row('📝Jugar📝')
botones_home.row('💰Balance💰', '📙Instrucciones📙')
botones_home.row('📥Depositos📥', '📤Retiros📤')



# Define la función que maneja el comando /start
@bot.message_handler(commands=["start"])
def saludo(message):
    # Busca el usuario en la base de datos
    user = users.find_one({'_id': message.chat.id})
    #user = message.chat.id
    print(user)
    
    # Si el usuario no existe en la base de datos, le pide que use el comando /reg para introducir sus datos
    if user == None:
        bot.send_message(message.chat.id, "Usa el comando /reg para introducir tus datos", reply_markup=botones_home)
    # Si el usuario ya existe en la base de datos, le da la bienvenida y le recuerda que puede usar los botones de inicio
    else:
        bot.send_message('873919300', f"Hola de nuevo, <b>{user['name']}</b>\nRecuerda que puedes usar los botones de inicio", parse_mode="html", reply_markup=botones_home)
        #bot.send_message('873919300', f"Hola de nuevo", parse_mode="html", reply_markup=botones_home)



# Inicia el registro de un usuario
@bot.message_handler(commands=["reg"])
def registro(message):
    # Habilita la respuesta obligatoria para la siguiente pregunta
    markup = ForceReply()
    # Pregunta el nombre del usuario
    msg = bot.send_message(message.chat.id, "¿Como te llamas?", reply_markup=markup)
    # Registra la siguiente función para manejar la respuesta
    bot.register_next_step_handler(msg, preguntar_edad)


# Pregunta la edad del usuario
def preguntar_edad(message):
    # Guarda el nombre del usuario en la variable global
    usuarios[message.chat.id] = {}
    usuarios[message.chat.id]["nombre"] = message.text
    # Habilita la respuesta obligatoria para la siguiente pregunta
    markup = ForceReply()
    # Pregunta la edad del usuario
    msg = bot.send_message(message.chat.id, "¿Cuántos años tienes?", reply_markup=markup)
    # Registra la siguiente función para manejar la respuesta
    bot.register_next_step_handler(msg, preguntar_sexo)


# Pregunta el sexo del usuario
def preguntar_sexo(message):
    # Si la respuesta no es un número, vuelve a preguntar la edad
    if not message.text.isdigit():
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "ERROR: Debes introducir un número.\n¿Cuántos años tienes?")
        bot.register_next_step_handler(msg, preguntar_sexo)
    # Si la respuesta es un número, guarda la edad y pregunta el sexo
    else:
        usuarios[message.chat.id]["edad"] = int(message.text)
        markup = ReplyKeyboardMarkup(
            # Habilita el teclado temporal
            one_time_keyboard=True, 
            # Establece el placeholder para el campo de entrada
            input_field_placeholder="Pulsa un botón",
            # Habilita el redimensionamiento del teclado
            resize_keyboard=True
            )
        # Agrega dos botones: "Hombre" y "Mujer"
        markup.add("Hombre", "Mujer")
        # Pregunta el sexo del usuario
        msg = bot.send_message(message.chat.id, '¿Cuál es tu sexo?', reply_markup=markup)
        # Registra la siguiente función para manejar la respuesta
        bot.register_next_step_handler(msg, guardar_datos_usuario)


# Guarda los datos del usuario en la base de datos
def guardar_datos_usuario(message):
    # Si la respuesta no es "Hombre" ni "Mujer", vuelve a preguntar el sexo
    if message.text != "Hombre" and message.text != "Mujer":
        msg = bot.send_message(message.chat.id, "ERROR: Sexo no válido.\nPulsa un botón")
        bot.register_next_step_handler(msg, guardar_datos_usuario)
    # Si la respuesta es "Hombre" o "Mujer", guarda el sexo y los demás datos del usuario en la base de datos
    else:
        usuarios[message.chat.id]["sexo"] = message.text
        # Crea un mensaje con los datos introducidos por el usuario
        texto = 'Datos introducidos:\n'
        texto+= f'<code>NOMBRE:</code> {usuarios[message.chat.id]["nombre"]}\n'
        texto+= f'<code>EDAD:</code> {usuarios[message.chat.id]["edad"]}\n'
        texto+= f'<code>SEXO:</code> {usuarios[message.chat.id]["sexo"]}'
        texto+= f'<code>ID:</code> {message.chat.id}'
        # Quita el teclado temporal
        markup = ReplyKeyboardRemove()
        # Muestra los datos al usuario y guarda los datos en la base de datos

        bot.send_message(message.chat.id, texto, parse_mode="html", reply_markup=markup)
        print(usuarios)

        #MONGO
        users.insert_one({
            '_id': message.chat.id,
            'name': usuarios[message.chat.id]["nombre"],
            'info': usuarios[message.chat.id]["edad"]
            })
        del usuarios[message.chat.id]

#FIN DE REGISTRO DE USUARIO


# Crear decorador para manejar el comando /charada
@bot.message_handler(commands=['charada'])
def charada_command(message):
    # Expresión regular para capturar el argumento después del comando
    pattern = re.compile(r'^/charada\s+(.*)$')
    match = pattern.match(message.text)

    # Si hay un argumento después del comando
    if match:
        argumento = match.group(1)
        if argumento.isdigit():
            result = charada_srch.buscar_numero(argumento)
        elif argumento.isalpha():
            result = charada_srch.buscar_charada(argumento)
        else:
            bot.send_message(message.chat.id, "El argumento no es ni un número ni un simbolo.")

        # Envía un mensaje al usuario con el resultado
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Debes proporcionar un argumento después del comando /charada")


#Funcion de botones

# Instrucciones
@bot.message_handler(regexp="📙Instrucciones📙")
def handle_instrucciones(message):
    # Envía un mensaje al usuario con "Blabla emojis"
    bot.send_message(message.chat.id, "Blabla emojis")

# Balance
@bot.message_handler(regexp="💰Balance💰")
def handle_balance(message):
    # Envía un mensaje al usuario con "Tienes un saldo total de: $.."
    bot.reply_to(message, "Tienes un saldo total de: $..")

# Depósitos
@bot.message_handler(regexp="📥Depositos📥")
def handle_depositos(message):
    # Envía un mensaje al usuario con "Blabla emojis"
    texto = charada.buscar_charada("sol")
    bot.send_message(message.chat.id, texto)

# Retiros
@bot.message_handler(regexp="📤Retiros📤")
def handle_retiros(message):
    # Envía un mensaje al usuario con "Blabla emojis"
    bot.send_message(message.chat.id, "Blabla emojis")

# Número
@bot.message_handler(regexp="Num")
def handle_numero(message):
    # Realiza una solicitud HTTP GET a la URL especificada y obtiene la respuesta como un diccionario de Python
    r = requests.get("https://2ih4c7nldh.execute-api.us-west-1.amazonaws.com/prod/last").json()

    # Convierte el número de la tarde a una lista de dígitos y elimina el primer dígito
    ndia = Convert(r['pick3Midday'])
    del ndia[0]

    # Convierte la lista de dígitos a una cadena
    ndia = listToString(ndia)

    # Si no hay un número para la noche, establece el texto del mensaje en un formato específico
    if r['pick4Evening'] == None:
        texto = f"La Bolita:\n\n<b>Día:</b> {ndia}\nFijo:{r['pick3Midday']}\nCorrido:{r['pick4Midday']}\n\n<b>Noche:</b> -\nFijo: -\nCorrido: -"
    else:
        # Si hay un número para la noche, convierte el número de la noche a una lista de dígitos y elimina el primer dígito
        nnoche = Convert(r['pick3Evening'])
        del nnoche[0]

        # Convierte la lista de dígitos a una cadena
        nnoche = listToString(nnoche)

        # Establece el texto del mensaje en un formato específico
        texto = f"La Bolita:\n\n<b>Día:</b> {ndia}\nFijo:{r['pick3Midday']}\nCorrido:{r['pick4Midday']}\n\n<b>Noche:</b> {nnoche}\nFijo:{r['pick3Evening']}\nCorrido:{r['pick4Evening']}"

    # Envía un mensaje al usuario con el texto formateado
    bot.send_message(message.chat.id, texto, parse_mode="html")




#INICIO JUEGO
@bot.message_handler(regexp="📝Jugar📝")
def juego(message):
    #Horario de juego de 9-1
    game[message.chat.id] = {}
    if((military_time >= 9 and military_time < 13) or (military_time >= 17 and military_time < 21) or 1 == 1):
        if(military_time >= 9 and military_time <= 13):
            game[message.chat.id]["horario"] = "Día"
        elif(military_time >= 17 and military_time <= 21 or 1==1):
            game[message.chat.id]["horario"] = "Noche"
        markup = ForceReply()
        print(game)
        msg = bot.send_message(message.chat.id, "¿Cuanto vas a jugar?", reply_markup=markup)
        bot.register_next_step_handler(msg, step_2)
    else:
        bot.send_message(message.chat.id, "No es horario de juego", reply_markup=botones_home)

def step_2(message):
    calvo = message.text
    items = calvo.split(',')
    items = [item.strip() for item in items]
    #Verificar que el formato (4-5) sea correcto
    contin = True
    for item in items:
    # Verificar el formato del elemento
        if "-" in item:
            # Dividir el elemento por el carácter "-"
            a, b = item.split('-')
            # Verificar si "a" y "b" son números enteros
            if a.isdigit() and b.isdigit():
                # Convertir "a" y "b" a números enteros
                a = int(a)
                b = int(b)
            else:
                # Añadir una tupla con una cadena de texto que indique que el formato no es correcto
                contin = False
        else:
            # Añadir una tupla con una cadena de texto que indique que el formato no es correcto
            contin = False
    if(contin == True):
        result = []
        for item in items:
            a, b = item.split('-')
            result.append((a, b))
        tuple = [(int(a), int(b)) for a, b in result]
        #guardar tupla
        game[message.chat.id]["tupla"] = [{'msg_id': 873919300, 'horario': game[message.chat.id]["horario"], 'a': a, 'b': b} for a, b in tuple]
        result = 0
        # Recorrido de la tupla
        for item in tuple:
            # Acceso al segundo elemento de cada tupla
            b = item[1]
            # Suma del elemento al resultado
            result += b

        saldo = 12
        markup = ForceReply()

    if (contin == False):
        bot.send_message(message.chat.id, "Formato erroneo", reply_markup=botones_home)
    elif (saldo >= result):
        markup = ReplyKeyboardMarkup(
            one_time_keyboard=True, 
            input_field_placeholder="Pulsa un botón",
            resize_keyboard=True
            )
        markup.add("Si", "No")
        msg = bot.send_message(message.chat.id, "Todo está listo ¿Quieres continuar?", reply_markup=markup)
        bot.register_next_step_handler(msg, step_3)
    else:
        bot.send_message(message.chat.id, "No dispones saldo suficiente para esta operación", reply_markup=botones_home)

def step_3(message):
    if message.text != "Si" and message.text != "No":
        msg = bot.send_message(message.chat.id, "ERROR: Opción no válida.\nPulsa un botón")
        bot.register_next_step_handler(msg, step_3)
    elif(message.text == "Si"):

        test.insert_many(game[message.chat.id]["tupla"])
        #compruebo de nuevo si es horario de juego
        if((military_time >= 9 and military_time < 13) or (military_time >= 17 and military_time < 21) or 1 == 1):
            texto = f'Listo ha jugado, {game[message.chat.id]["horario"]}!'
            bot.send_message(message.chat.id, texto, reply_markup=botones_home)
        else:
            bot.send_message(message.chat.id, "No es horario de juego", reply_markup=botones_home)
    elif(message.text == "No"):
        bot.send_message(message.chat.id, "Juego Cancelado!", reply_markup=botones_home)

#FIN DE JUEGO



# Define una función de tarea programada
def scheduled_task():
    r = requests.get("https://2ih4c7nldh.execute-api.us-west-1.amazonaws.com/prod/last")
    r = r.json()
    #convertir fijo dia
    ndia = Convert(r['pick3Midday'])
    del ndia[0]
    ndia = listToString(ndia)
    print(r['pick4Evening'])
    if r['pick4Evening'] == None:
        texto = f"La Bolita:\n\n<b>Día:</b> {ndia}\nFijo:{r['pick3Midday']}\nCorrido:{r['pick4Midday']}\n\n<b>Noche:</b> -\nFijo: -\nCorrido: -"
    else:
        #convertir fijo noche
        nnoche = Convert(r['pick3Evening'])
        del nnoche[0]
        nnoche = listToString(nnoche)
        texto = f"La Bolita:\n\n<b>Día:</b> {ndia}\nFijo:{r['pick3Midday']}\nCorrido:{r['pick4Midday']}\n\n<b>Noche:</b> {nnoche}\nFijo:{r['pick3Evening']}\nCorrido:{r['pick4Evening']}"
    bot.send_message(873919300, texto, parse_mode="html")

# Crea una instancia de BackgroundScheduler
scheduler = BackgroundScheduler()

# Obtiene una instancia de pytz para la zona horaria deseada
tz = pytz.timezone('Cuba')

# Programa la tarea para que se ejecute cada hora CronTrigger(hour=22, minute=34, timezone=tz)
scheduler.add_job(scheduled_task, CronTrigger(hour=14, minute=30, timezone=tz))
scheduler.add_job(scheduled_task, CronTrigger(hour=22, minute=30, timezone=tz))

# Inicia el scheduler
scheduler.start()

# Crea un hilo para ejecutar la función infinity_polling en segundo plano
print("Iniciando Servidor")
while True:
    try:
        # Realiza el bucle de polling
        bot.infinity_polling()
    except Exception as e:
        # Si se produce un error, muestra un mensaje y vuelve a intentar
        print(f'Error: {e}')
        continue
#polling_thread = threading.Thread(target=bot.polling)
#polling_thread.start()