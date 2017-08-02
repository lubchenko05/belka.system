# -*- coding: utf-8 -*-
import telebot
import codecs
import time
from flask import Flask, render_template, session, redirect, url_for, escape, request, jsonify
import threading
import time
from hashlib import sha256
import string
import random
import urllib.request

import settings
from logic.user import User
from logic.event import Event

global hashs_for_users
hashs_for_users = {}


help_text = codecs.open("templates/help.md", "r", "utf_8_sig" ).read()

def main_menu(chatId):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Ближайшие Мероприятия', 'Я не знаю что тут будет')
    user_markup.row('Расписание Работы','Контакты')
    try:
        bot.send_message(chatId, 'Главное меню', reply_markup=user_markup)
    except:
        print(f"{chatId} - chat_id not found")

bot = telebot.TeleBot(settings.TOKEN)



# users = User.all_user()
# for user in users:
#     print(user)
#     main_menu(user.chat_id)

@bot.message_handler(commands=['start'])
def start_command(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser != None):
        bot.send_message(message.from_user.id, 'Ой да бросьте, вы уже не первый раз у нас.')
        main_menu(message.chat.id)
    else:
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        button_phone = telebot.types.KeyboardButton(text="Зарегистрироваться", request_contact=True)
        user_markup.add(button_phone)
        bot.send_message(message.from_user.id, 'Вас привествуют и просят зарегесрироваться', reply_markup=user_markup)

@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton('Message the developer', url='telegram.me/YurijL'),
        telebot.types.InlineKeyboardButton('Message the general director', url='telegram.me/arudik'),
        telebot.types.InlineKeyboardButton('Message the event manager', url='telegram.me/gorod_d')
    )
    bot.send_message(message.chat.id, help_text, reply_markup=keyboard)

# Зарегистрироваться - пересылка контактов пользователя
@bot.message_handler(content_types=['contact'])
def handle_text(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    # свои ли контакты переслал пользователь?
    if (message.from_user.id == message.contact.user_id):
        # может мы его уже знаем?
        if (cuser != None):
            return
        # ну лан так и быть зарегистрируем его
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        phone = message.contact.phone_number
        chat_id = message.chat.id
        username = message.from_user.username
        cuser = User.registration(first_name, last_name, phone, chat_id, username)
        main_menu(message)

####
#   main_menu
####
@bot.message_handler(func=lambda mess: "Ближайшие Мероприятия" == mess.text, content_types=['text'])
def handle_text(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser == None):
        start_command(message)
        return
    events = Event.all_event()
    list_of_users_event = []
    cuser_events = cuser.get_events()
    for cuser_event in cuser_events:
        list_of_users_event.append(cuser_event._id)
    #print(list_of_users_event)
    for event in events:
        text = 'Записаться'
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        for cuser_event_id in list_of_users_event:
            if (str(cuser_event_id) == str(event._id)): text = 'Отписаться'
        keyboard.add(
            telebot.types.InlineKeyboardButton(text, callback_data=f"{event._id}")
        )
        bot.send_message(message.chat.id, f"{event.date} {event.time} - {event.title}\n {event.description}",
            disable_web_page_preview=True, reply_markup=keyboard)

@bot.message_handler(func=lambda mess: "Расписание Работы" == mess.text, content_types=['text'])
def work_schedule(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser == None):
        start_command(message)
        return
    bot.send_message(message.chat.id, 'Расписание Работы:\nПн.-Пт. 14:30 - 22:00\nСб. 12:00 - 22:00\nМожливі перерви у роботі простору в зв\'язку з проведенням заходів.')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    cuser = User.get_user('chat_id', call.message.chat.id)
    # Если сообщение из чата с ботом
    if call.message:
        events =  Event.all_event()

        list_of_users_event = []
        cuser_events = cuser.get_events()
        for cuser_event in cuser_events:
            list_of_users_event.append(cuser_event._id)

        for event in events:
            is_delete_event = False
            if call.data == str(event._id):
                for cuser_event in cuser_events:
                    if (str(cuser_event._id) == str(event._id)): is_delete_event = True
                if (is_delete_event) :
                    cuser.decline_event(event._id)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Отписан  на {event.title}")
                else:
                    cuser.accept_event(event._id)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Записан на {event.title}")
    # Если сообщение из инлайн-режима
    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Вы записаны")

def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60) #constantly get messages from Telegram
    except:
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()

class BotThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False
    def run(self):
        telegram_polling()

bot_thread = BotThread()
bot_thread.start()

web = Flask(__name__)

web.secret_key = '6579af11e0922f02be35da90481274b93fc9b26c6c8a9602f34c6437'
web.config['SESSION_TYPE'] = 'memcache'

@web.route('/login')
def login():
    return render_template('login.html')

@web.route('/')
def index():
    if 'username' in session:
        cuser = User.get_user('username',session['username'])
        if (cuser != None):
            avatar = bot.get_user_profile_photos(cuser.chat_id, limit=1)
            avatar_path = bot.get_file(avatar.photos[0][0].file_id).file_path
            urllib.request.urlretrieve('https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, avatar_path), f'./static/img/avatar/{cuser.username}.png')
            data = {}
            count = 0
            count = len(User.all_user());
            # for user in User.all_user():
            #     count += 1
            data['total_users'] = count


            return render_template('index.html', username=f'{cuser.username}', data=data)
        return redirect(url_for('login'))
        session['username'] = None
    else:
        return redirect(url_for('login'),code=302)

@web.route('/', methods=['POST'])
def indexPost():
    global hashs_for_users
    if request.method == 'POST':
        if ((request.form['username'] != None)):
            cuser = User.get_user('username', f"{request.form['username']}")
            if (cuser != None):
                if ((hashs_for_users[cuser.chat_id] == request.form['rcode']) & (hashs_for_users[cuser.chat_id] != None) & (hashs_for_users[cuser.chat_id] != '')):
                    bot.send_message(chat_id=cuser.chat_id, text=f'success')
                    session['username'] = request.form['username']
                    return render_template('index.html',username=f'{cuser.username}')
    return redirect(url_for('login'), code=302)


@web.route('/login2', methods=['GET', 'POST'])
def login2():
    global hashs_for_users
    if request.method == 'POST':
        if (request.form['username'] != None ):
            cuser = User.get_user('username', f"{request.form['username']}")
            if (cuser != None):
                if (cuser.is_staff == True):
                    char_set = string.ascii_letters + string.digits;
                    hash = sha256((''.join(random.sample(char_set * 100, 256))).encode("utf-8")).hexdigest()
                    hashs_for_users[cuser.chat_id]= hash
                    bot.send_message(chat_id=cuser.chat_id, text=f'your key: {hash}')
                    return render_template('login2.html',username=f"{cuser.username}")
    return redirect(url_for('login'))


@web.route('/users')
def users():
    users = User.all_user()
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('users.html',username=f'{cuser.username}',users = users)
    return redirect(url_for('login'))


@web.route('/deleteUser', methods=['GET'])
def deleteUser():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.delete_user()
                return "ok"
    return redirect(url_for('login'))


@web.route('/makeStaffUser', methods=['GET', 'POST'])
def makeStaffUser():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.is_staff = 1
                        user.update()
                return "ok"
    return redirect(url_for('login'))

@web.route('/unStaffUser', methods=['GET', 'POST'])
def unStaffUser():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.is_staff = 0
                        user.update()
                return "ok"
    return redirect(url_for('login'))

@web.route('/events')
def events():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('events.html',username=f'{cuser.username}')
    return redirect(url_for('login'))

@web.route('/sendtoall', methods=['GET', 'POST'])
def sendtoall():
    if request.method == 'POST':
        if (request.form['text'] != None):
            users = User.all_user()
            for user in users:
                bot.send_message(user.chat_id, f"{request.form['text']}")
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('sendtoall.html',username=f'{cuser.username}')
    return redirect(url_for('login'))



web.run(debug=False, host='0.0.0.0')

# _______********1*888888888801****__________
# ______*1000018111****10088888888*__________
# ______*0000118011*1***0*81*108888*_________
# ______*0811088011100888081****1188**_______
# _______*0****0*****08888888880110811_______
# ________*0***0***_**1118888888888880*______
# _________18**1*1**0*1110008888888881*______
# _________**801*******0018888888888**_______
# ___________*880110*****88888888881*________
# _____________001*******1088888880**________
# ____________*0888******1*8888881**_________
# ____________*188801****0*08888880*_________
# __________**1***0011***1**88888*___________
# _________*0******11*******88080*___________
# ________*8*********1***011****_____________
# _______*181***********111*_________________
# _____*1100**********080*___________________
# ____*01************181*____________________
# ___*811************11*_____________________
# ____*10011*****1*111*______________________
# ______*881********1*_______________________
# ______*8800******10*_______________________
# ______*88011**1**0*________________________
# _______88011111*181*_______________________
# _______*8810111*1080*______________________
# ________88000111110081*____________________
# ________*888800111111081*__________________
# ________*088880111**11108*_________________
# _________*88888011****1100*________________
# __________*88880011****118*________________
# ___________18888011***11100________________
# ____________*880011***11181________________
# ___________*08801111111118*________________
# __________*088801111111108_________________
# ________**8888001111111181_________________
# ________*8808800111111108*_________________
# ______*188011880111111108*_________________
# _____*180011*880111111100______****________
# _____18011***080111111100___***00101*11110*
# ____10011***188001111108111000111*108*****_
# ___*811***108880011111000011*1101***1881**_
# _**011***1881*80011111080111000800001*1*10*
# _*101***181***80011111088011*******11008101
# _*0111**1*1110800111108*_______________1810
# _*011011110888811111180_________________*00
# __*10088801**_800111080__________________**
# ______________*8801*180____________________
# _______________18011188*___________________
# _______________*80111181___________________
# ________________08111118*__________________
# ________________*81111181__________________
# ________________*80111100__________________
# _________________00111*00__________________
# _________________18111*00__________________
# _________________*8111*01__________________
# __________________8111*8*__________________
# __________________00*1*8*__________________
# __________________00*108*__________________
# __________________10*180___________________
# __________________101*81___________________
# __________________101100___________________
# _________________*0111081*_________________
# _________________*81008810_________________
# _________________*80008108*________________
# _________________181001080_________________
# _________________18011818*_________________
# ________________1088110*8*_________________
# ______________10080008**8*_________________