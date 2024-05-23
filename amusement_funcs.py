import telebot
from telebot import types
from datetime import datetime
from decouple import config
import random
from helpedit_funcs import push_smth


catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)


def randomizer(file):
    with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
        list = file.read().split("\n")
        return random.choice(list)


def amusement_choice(type, message):
    kind = randomizer(f'amusement/{type}_kind')
    cringe = randomizer(f'amusement/{type}_cringe')
    evil = randomizer(f'amusement/{type}_evil')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(kind, callback_data="kind_1"))
    markup.add(types.InlineKeyboardButton(cringe, callback_data="cringe_1"))
    markup.add(types.InlineKeyboardButton(evil, callback_data="evil_1"))
    push_smth("temp_name", f'{kind}/{cringe}/{evil}', message.chat.id)

    bot.send_message(message.chat.id, 'Что у нас на сегодня?', reply_markup=markup)


def fun_choice(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Смотреть фильм", callback_data="film"))
    markup.add(types.InlineKeyboardButton("Читать книги", callback_data="book"))
    markup.add(types.InlineKeyboardButton("Слушать музыку", callback_data="music"))
    markup.add(types.InlineKeyboardButton("Смотреть ютубчик", callback_data="youtube"))
    markup.add(types.InlineKeyboardButton("Смотреть сериальчик", callback_data="series"))
    markup.add(types.InlineKeyboardButton("Смотреть мультики", callback_data="cartoon"))
    markup.add(types.InlineKeyboardButton("Играть в игры", callback_data="game"))

    bot.send_message(message, 'Чем сегодня займёмся?', reply_markup=markup)


# запись времени начала развлечения в бд
def amuse_time_push(id):
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    push_smth('amuse_timestamp', time, id)