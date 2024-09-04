import telebot
from telebot import types
from datetime import datetime
from decouple import config
import random
import time

from feeding_funcs import time_check
from helpedit_funcs import push_smth, get_smth

catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)

def amuse_list(shortlist, text, message):
    markup = types.InlineKeyboardMarkup()
    if shortlist == "full":
        markup.add(types.InlineKeyboardButton("Смотреть фильм", callback_data="film"))
        markup.add(types.InlineKeyboardButton("Читать книги", callback_data="book"))
        markup.add(types.InlineKeyboardButton("Слушать музыку", callback_data="music"))
        markup.add(types.InlineKeyboardButton("Смотреть ютубчик", callback_data="youtube"))
        markup.add(types.InlineKeyboardButton("Смотреть сериальчик", callback_data="series"))
        markup.add(types.InlineKeyboardButton("Смотреть мультики", callback_data="cartoon"))
        markup.add(types.InlineKeyboardButton("Играть в игры", callback_data="game"))
    else:
        for a in shortlist:
            if a == "f":
                markup.add(types.InlineKeyboardButton("Смотреть фильм", callback_data="film"))
            elif a == "b":
                markup.add(types.InlineKeyboardButton("Читать книги", callback_data="book"))
            elif a == "m":
                markup.add(types.InlineKeyboardButton("Слушать музыку", callback_data="music"))
            elif a == "y":
                markup.add(types.InlineKeyboardButton("Смотреть ютубчик", callback_data="youtube"))
            elif a == "s":
                markup.add(types.InlineKeyboardButton("Смотреть сериальчик", callback_data="series"))
            elif a == "c":
                markup.add(types.InlineKeyboardButton("Смотреть мультики", callback_data="cartoon"))
            elif a == "g":
                markup.add(types.InlineKeyboardButton("Играть в игры", callback_data="game"))

    bot.send_message(message, text, reply_markup=markup)

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

    n = get_smth('action_number', message.chat.id)
    stage = get_smth('stage', message.chat.id)
    if n == 4 and stage == 1 and type != "game":
        bot.send_message(message.chat.id, 'Пожалуй, остановлюсь на...', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Что у нас на сегодня?', reply_markup=markup)


def fun_choice(message):
    n = get_smth('action_number', message)
    stage = get_smth('stage', message)
    markup = types.InlineKeyboardMarkup()
    if n == 4 and stage == 1:
        last_amusement = get_smth("last_amuse_type", message)
        if last_amusement == "film":
            time = 3
        elif last_amusement == "youtube":
            time = 2
        else:
            time = 1.5

        if time_check("amuse", time, message) == 0:
            bot.send_message(message,
                             "Ребята всё ещё заняты. Пожалуйста, попробуйте позже.")

        else:
            markup.add(types.InlineKeyboardButton("*пойти домой*", callback_data="go_home"))
            markup.add(types.InlineKeyboardButton("*найти чем еще развлечься*", callback_data="stay_in_lab"))

            bot.send_message(message, 'Замечательно, профессор будет в восторге. Что бы теперь поделать?',
                             reply_markup=markup)

    else:
        amuse_list("full", 'Чем сегодня займёмся?', message)




# запись времени начала развлечения в бд
def amuse_time_push(id):
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    push_smth('amuse_timestamp', time, id)