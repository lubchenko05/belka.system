# -*- coding: utf-8 -*-
import telebot
import settings
import codecs

help_text = codecs.open( "templates/help.md", "r", "utf_8_sig" ).read()

bot = telebot.TeleBot(settings.TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        help_text
    )

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

bot.polling(none_stop=True)
