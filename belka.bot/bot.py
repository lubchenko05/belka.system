# -*- coding: utf-8 -*-
import telebot
import codecs

import time
from sqlalchemy.sql.functions import current_user

import settings
from logic.user import User
from logic.event import Event
help_text = codecs.open("templates/help.md", "r", "utf_8_sig" ).read()

# user_state_dict['chatid'] = STATE
# 0 - Главное меню
# 1 - Записаться на ивент
# 2 -
# 10 - Admin menu
user_state_dict = {}

bot = telebot.TeleBot(settings.TOKEN)

users = User.all_user()
for user in users:
    #bot.send_message(user.chat_id, 'НЛО прилетело, и оставило это сообщение…')
    user_state_dict[user.chat_id] = 0
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Ближайшие Мероприятия', 'Я не знаю что тут будет')
    user_markup.row('Расписание Работы','Контакты')
    try:
        bot.send_message(user.chat_id, 'я Обновилсо', reply_markup=user_markup)
    except:
        print(f"{user.chat_id} - chat_id not found")

def user_identify(message):
    # зачем я это делал? наверное был я бухой ...
    cuser = None
    if (User.get_user('chat_id', message.from_user.id) != None):
        cuser = User.get_user('chat_id', message.from_user.id)
    return cuser

def main_menu(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    user_state_dict[cuser.chat_id] = 0
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Ближайшие Мероприятия', 'Записаться на Мероприятие')
    user_markup.row('Расписание Работы','Контакты')
    bot.send_message(message.from_user.id, 'Главное меню.', reply_markup=user_markup)





def admin_menu(message):
    cuser = user_identify(message)
    user_state_dict[cuser.chat_id] = 10
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Добавить ивент', 'Отменить ивент')
    user_markup.row('Добавить админа','Удалить админа')
    user_markup.row('Выйти из админки')
    bot.send_message(message.from_user.id, 'Админское меню.', reply_markup=user_markup)

@bot.message_handler(commands=['start'])
def start_command(message):
    cuser = user_identify(message)
    if (cuser != None):
        bot.send_message(message.from_user.id, 'Ой да бросьте, вы уже не первый раз у нас.')
        main_menu(message)
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
    cuser = user_identify(message)
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
    if(user_state_dict[cuser.chat_id] != 0):
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


@bot.message_handler(func=lambda mess: "Записаться на Мероприятие" == mess.text, content_types=['text'])
def handle_text(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser == None):
        start_command(message)
        return
    if(user_state_dict[cuser.chat_id] != 0):
        return
    user_state_dict[cuser.chat_id] = 1
    bot.send_message(message.chat.id,'1 - 29.06.2017 19:00 - Falling Walls Lab')
    bot.send_message(message.chat.id,'2 - 30.06.2017 19:00 - Falling Walls Lab')
    bot.send_message(message.chat.id,'3 - 01.07.2017 19:00 - Falling Walls Lab')
    bot.send_message(message.chat.id,'4 - 02.07.2017 19:00 - Falling Walls Lab')
    bot.send_message(message.chat.id, 'введите номер меропрятия на которое вы хоите записаться')

@bot.message_handler(func=lambda mess: "Расписание Работы" == mess.text, content_types=['text'])
def work_schedule(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser == None):
        start_command(message)
        return
    bot.send_message(message.chat.id, 'Расписание Работы:\nПн.-Пт. 14:30 - 22:00\nСб. 12:00 - 22:00\nМожливі перерви у роботі простору в зв\'язку з проведенням заходів.')

#####
#   Админка
#####

@bot.message_handler(func=lambda mess: "Админка" == mess.text, content_types=['text'])
def handle_text(message):
    cuser = user_identify(message)
    if (cuser == None):
        start_command(message)
        return
    if (cuser.is_staff == 0):
        main_menu(message)
        return
    user_state_dict[cuser.chat_id] = 10
    bot.send_message(message.chat.id, f"Приветствуем вас в админке уважаемый {cuser.first_name} {cuser.last_name}")
    admin_menu(message)


@bot.message_handler(func=lambda mess: "Добавить ивент" == mess.text, content_types=['text'])
def handle_text(message):
    cuser = user_identify(message)
    if (cuser == None):
        start_command(message)
        return
    if (cuser.is_staff == 0):
        main_menu(message)
        return
    if (user_state_dict[cuser.chat_id] != 10):
        return
    bot.send_message(message.chat.id, "ивент добавить захотели?")


@bot.message_handler(func=lambda mess: "Отменить ивент" == mess.text, content_types=['text'])
def handle_text(message):
    global cuser
    if (cuser == None): user_identify(message)
    if (cuser == None): start_command(message)
    if (cuser.is_staff == 0):
        main_menu(message)
        return

@bot.message_handler(func=lambda mess: "Добавить админа" == mess.text, content_types=['text'])
def handle_text(message):
    global cuser
    global AddAdminStep
    if (cuser == None): user_identify(message)
    if (cuser == None): start_command(message)
    if (cuser.is_staff == 0):
        main_menu(message)
        return
    AddAdminStep = 1

# В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
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

# обработка всех сообщений пользователя
@bot.message_handler(func=lambda mess: True)
def echo_all(message):
    cuser = User.get_user('chat_id', message.from_user.id)
    if (cuser == None): return
    # Записаться на Мероприятие
    if(user_state_dict[cuser.chat_id] == 1):
        bot.send_message(message.chat.id, f"Вы написали {message.text}")
        main_menu(message)
        return
    #bot.reply_to(message, 'text', disable_web_page_preview=True)

def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60) #constantly get messages from Telegram
    except:
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()

telegram_polling()