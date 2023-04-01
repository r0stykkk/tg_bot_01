import hashlib
import telebot
import sqlite as s
import os
import uuid
from sqlite import conn, cursor
from telebot import types

bot = telebot.TeleBot("6188033224:AAHuZgBFucFyB79H2UA3SPWfXSaNtK3yyq0")

def key(password, salt):
    keyF = hashlib.sha256((password + salt).encode()).hexdigest()
    return keyF
def logpass(password, salt, keyp):
    if password == key(keyp, salt):
        return True
    else:
        return False
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Авторизация':
        login(message)
    elif message.text == 'Регистрация':
        check(message)
    elif message.text == 'Действие':
        vibor(message)
    elif message.text == '/start':
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, text='Неизвестная команда!')

@bot.message_handler(commands=['choice'])
def vibor(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Статистика")
    btn2 = types.KeyboardButton("Время работы")
    btn3 = types.KeyboardButton("Что делает")
    btn4 = types.KeyboardButton("Время в пр-ях")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.from_user.id, "Смотрите действия в кнопках", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Авторизация")
    btn2 = types.KeyboardButton("Регистрация")
    btn3 = types.KeyboardButton("Выбор сотрудника")
    btn4 = types.KeyboardButton("Действие")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.from_user.id, "Привет! 👋", reply_markup=markup)

@bot.message_handler(commands=['reg'])
def check(message):
    user_id = message.from_user.id
    if s.getTrue(user_id=user_id) is False:
        mes = bot.send_message(message.chat.id, text='Введите желаемый пароль')
        bot.register_next_step_handler(mes, reg)
    else:
        bot.send_message(message.chat.id, text='Вы зарегистрированы ')
        if s.getName(conn=conn, user_id=user_id) is None:
            mes = bot.send_message(message.chat.id, text='Но вы не ввели пароль. \n Введите желаемый пароль')
            bot.register_next_step_handler(mes, pass_set)
def reg(message):
    user_id = message.from_user.id
    username = message.from_user.username
    salt = uuid.uuid4().hex
    password = message.text
    passw = key(password, salt)
    s.db_table_val(user_id=user_id, username=username, passw=passw, salt=salt)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, text='Вы зарегистрированы ')
def pass_set(message):
    user_id = message.from_user.id
    username = message.from_user.username
    salt = uuid.uuid4().hex
    password = message.text
    passw = key(password, salt)
    s.db_table_ed(passw=passw, user_id=user_id)
    s.db_table_ed2(salt=salt, user_id=user_id)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, text='Вы установили пароль')


@bot.message_handler(commands=['login'])
def login(message):
    user_id = message.from_user.id
    username = message.from_user.username
    mes = bot.send_message(message.chat.id, text='Введите пароль, пожалуйста')
    bot.register_next_step_handler(mes, get_password)
def get_password(message):
    user_id = message.from_user.id
    username = message.from_user.username
    passw = s.getName(conn=conn, user_id=user_id)
    salt = s.getSalt(conn=conn, user_id=user_id)
    result = logpass(passw, salt, message.text)
    if result is True:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "Пароль верный!")
    else:
        mes = bot.send_message(message.chat.id, text='Неверный пароль, попробуйте еще раз')
        bot.register_next_step_handler(mes, get_password)


bot.infinity_polling()