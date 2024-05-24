import telebot
from telebot import types
import sqlite3
from decouple import config


catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)


# получаем имя пользователя
def user(message):
    return " ".join(filter(lambda x: x, [message.from_user.first_name, message.from_user.last_name]))


# достаём текст из файла, если есть выборы то делаем словарь
# {текст кнопки: колбек данные}
def texts(file: str):
    if file.find('lines_buttons/c') != -1:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            lines = file.read().split("\n")
            d = {}
            for line in lines:
                button_text, cb = line.split(";")
                d[button_text] = cb
            return d
    else:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            return file.read()


def invert(file):
    if str(file).find('lines_buttons/c') != -1:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            lines = file.read().split("\n")
            d = {}
            for line in lines:
                button_text, cb = line.split(";")
                d[cb] = button_text
            return d


# функция для редактирования сообщений (два фрагмента текста совмещает в один)
def joiner(text1, text2, NeedTexts=True) -> str:
    if not NeedTexts:
        return f'{text1}\n\n{text2}'
    return f"{texts(text1)}\n\n{texts(text2)}"


def format_replace(line, d):
    for key, value in d.items():
        line = line.replace("{" + key + "}", value)
    return line


# достать значение из бд
def get_smth(column, id):
    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute(f'SELECT {column} FROM users WHERE id = ?', (id,))
    value = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return value


# записать значение в бд
def push_smth(column, value, id):
    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET {column} = ? WHERE id = ?', (value, id))
    conn.commit()
    cur.close()
    conn.close()


def choice(message, n):
    markup = types.InlineKeyboardMarkup()
    for var, cb in texts(f"lines_buttons/c{n}").items():
        markup.add(types.InlineKeyboardButton(str(var), callback_data=cb))
    bot.send_message(message.chat.id, texts(f"lines_direct/{n}"), reply_markup=markup)