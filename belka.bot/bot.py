# -*- coding: utf-8 -*-
import telebot
import codecs

from sqlalchemy.sql.functions import current_user

import settings
from logic.user import User
help_text = codecs.open("templates/help.md", "r", "utf_8_sig" ).read()

cuser = None # current user

bot = telebot.TeleBot(settings.TOKEN)
user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
button_phone = telebot.types.KeyboardButton(text="Зарегистрироваться", request_contact=True)
user_markup.add(button_phone)

def main_menu(message):
    global cuser;
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Расписание Мероприятий', 'Предложить Мероприятие')
    user_markup.row('Расписание Работы','выведи про меня инфу')
    user_markup.row('Как к нам добраться?')
    if (cuser.is_staff == True):
        user_markup.row('Админка')
    bot.send_message(message.from_user.id, 'Главное меню.', reply_markup=user_markup)


@bot.message_handler(commands=['start'])
def start_command(message):
    global cuser
    if (User.get_user('chat_id', message.from_user.id) != None):
        cuser = User.get_user('chat_id', message.from_user.id)
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
        telebot.types.InlineKeyboardButton(
            'Message the developer', url='telegram.me/YurijL'
        ),
        telebot.types.InlineKeyboardButton(
            'Message the general director', url='telegram.me/arudik'
        ),
        telebot.types.InlineKeyboardButton(
            'Message the event manager', url='telegram.me/gorod_d'
        )
    )
    bot.send_message(
    message.chat.id,
    help_text,
    reply_markup=keyboard
    )

@bot.message_handler(content_types=['contact'])
def handle_text(message):
    global cuser
    if (message.from_user.id == message.contact.user_id):
        if (User.get_user('chat_id',message.contact.user_id) != None):
            return
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        phone = message.contact.phone_number
        chat_id = message.chat.id
        username = message.from_user.username
        cuser = User.registration(first_name, last_name, phone, chat_id, username)
        main_menu(message)

@bot.message_handler(func=lambda mess: "Расписание Мероприятий" == mess.text, content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, 'Пусо')

@bot.message_handler(func=lambda mess: "Предложить Мероприятие" == mess.text, content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, 'пишите на почту')

@bot.message_handler(func=lambda mess: "Как к нам добраться?" == mess.text, content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, 'пишком')

@bot.message_handler(func=lambda mess: "выведи про меня инфу" == mess.text, content_types=['text'])
def handle_text(message):
    global cuser
    if (cuser == None): return
    bot.send_message(message.chat.id, f"{cuser.first_name} {cuser.last_name}")


bot.polling(none_stop=True)