import telebot
from telebot import types
import sqlite3
import time

bot = telebot.TeleBot('6595427590:AAEWir1FTJpltWi2B1SIbBokhs7rSRSe7Rk')

def user(message):  # получаем имя пользователя
    return " ".join(filter(lambda x:x, [message.from_user.first_name, message.from_user.last_name]))


def texts(file):        # достаём текст из файла, если есть выборы то делаем словарь {текст кнопки: колбек данные}
    if file.find('lines_buttons/c') != -1:
        with open(f"scenario/{file}", "r", encoding="UTF-8") as file:
            l = file.read().split("\n")
            d = {}
            for line in l:
                button_text, cb = line.split(";")
                d[button_text] = cb
            return d
    else:
        with open(f"scenario/{file}", "r", encoding="UTF-8") as file:
            return file.read()

def joiner(text1, text2) -> str:       # функция для редактирования сообщений (два фрагмента текста совмещает в один)
    return f"{texts(text1)}\n\n{texts(text2)}"

def format_replace(line, d):
    for key, value in d.items():
        line = line.replace("{" + key + "}", value)
    return line


@bot.message_handler(commands=['start'])  # ответ на команду /start - соо от бота
def start_message(message):
    d = {"user":user(message)}
    bot.send_message(message.chat.id, format_replace(texts("commands/hello.txt"), d), parse_mode="HTML")


@bot.message_handler(commands=['contact'])     #ответ на команду /contact - соо от бота + пересылка соо от пользователя создателям
def contact_message(message):
    bot.send_message(message.chat.id, texts("commands/contact.txt"))
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):             #надо всё-таки решить, что эта команда делает и кому сообщение отправляет (или записывает ответы пользователей?)
        bot.reply_to(message, 'Ваше сообщение доставлено!')
        bot.send_message(416671069, f'{message.text}, от {user(message)}; ID: {message.from_user.id}')

@bot.message_handler(commands=['newgame'])    #ответ на команду /newgame 
def newgame_message(message):

    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id varchar(16) PRIMARY KEY, action_number int, current_time varchar(20))')
    cur.execute(f'INSERT INTO users (id, action_number, current_time) VALUES ({message.from_user.id}, 1, CURRENT_TIMESTAMP) ON CONFLICT (id) DO UPDATE SET id = {message.from_user.id}, action_number = 1, current_time = CURRENT_TIMESTAMP')
    conn.commit()
    cur.close()
    conn.close()

    i = 4
    for k in range(0,3):    # обратный отсчет
        i -= 1
        bot.send_message(message.chat.id, str(i))
        time.sleep(1)
    bot.send_message(message.chat.id, "Поехали!")
    make_action(message, 1, False)


def make_action(message, n: int, NeedPhoto: bool):    # считывает линейные действия
    if n == 10:
        bot.send_message(message.chat.id, texts("lines_direct/10_1.txt"))
    # надо не забыть присылать фоту если мы делаем ретерн чойс как у действия 6
    if n in [6, 10]:
        return choice(message, n)
    if n > 10:
        bot.send_message(message.chat.id, "<i>кто прочитал тот сдох...(с вас 5 рублей)</i>", parse_mode="HTML")
    else:
        if n == 4:
            bot.send_message(message.chat.id, "Ну конечно. На обратной стороне было неприлично много писанины:")
            time.sleep(2)
        if NeedPhoto:
            photo = open(f'scenario/photos/{n}.png', 'rb')
            bot.send_photo(message.chat.id, photo)
            time.sleep(5)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(texts(f"lines_buttons/b{n}.txt"), callback_data="next"))
        bot.send_message(message.chat.id, texts(f"lines_direct/{n}.txt"), reply_markup=markup)


def choice(message, n):
    markup = types.InlineKeyboardMarkup()
    for var, cb in texts(f"lines_buttons/c{n}.txt").items():
        markup.add(types.InlineKeyboardButton(str(var), callback_data=cb))
    bot.send_message(message.chat.id, texts(f"lines_direct/{n}.txt"), reply_markup=markup)

def get_n(id):
    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute(f'SELECT action_number FROM users WHERE id = {id}')
    n = cur.fetchall()[0][0]
    conn.commit()
    cur.close()
    conn.close()
    return n


@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):
    global response

    n =  get_n(callback.message.chat.id)

    if callback.data == "next":
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=joiner((f'lines_direct/{n}.txt'), (f'lines_buttons/b{n}.txt')))
        n += 1

        conn = sqlite3.connect('tbdatabase.db')
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET action_number = {n} WHERE id = {callback.message.chat.id}')
        conn.commit()
        cur.close()
        conn.close()

        if n in [2, 3, 4, 5, 6, 8]:
            make_action(callback.message, n, True)
        else:
            make_action(callback.message, n, False)

    if callback.data == 'film_starting':
        response = 'глянем. Господи, куда тебе показывать-то...'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/6.txt')}\nПосмотрим фильм!")
    if callback.data == 'book_starting':
        response = 'почитаем.'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/6.txt')}\nЧто-нибудь почитаем!")
    if callback.data == 'music_starting':
        response = 'послушаем.'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/6.txt')}\nПослушаем музыку!")
    if callback.data in ['music_starting', 'book_starting', 'film_starting']:
        n += 1
        make_action(callback.message, n, False)
    if callback.data == 'kind_3':
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/10.txt')}\n\n*Поменять воду*")
        res = 'Надеюсь, что обошлось.'
    if callback.data == 'cringe_3':
        res = 'И так сойдёт.'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/10.txt')}\n\n*Оставить как есть*")
    if callback.data == 'evil_3':
        res = 'В целом, ему нужнее.'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f"{texts('lines_direct/10.txt')}\n\n*Долить остатки*")
    if callback.data[-1] == "3":
        bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')
        n += 1
        make_action(callback.message, n, False)


bot.infinity_polling()
