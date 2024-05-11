import telebot
from telebot import types
import sqlite3
import time

bot = telebot.TeleBot('6595427590:AAEWir1FTJpltWi2B1SIbBokhs7rSRSe7Rk')


def user(message):  # получаем имя пользователя
    return " ".join(filter(lambda x:x, [message.from_user.first_name, message.from_user.last_name]))


def texts(file):
    with open(file, "r", encoding="UTF-8") as file:
        return file.read()


def format_replace(line, d):
    for key, value in d.items():
        line = line.replace("{" + key + "}", value)
    return line


@bot.message_handler(commands=['start'])  # ответ на команду /start - соо от бота
def start_message(message):
    d = {"user":user(message)}
    bot.send_message(message.chat.id, format_replace(texts("scenario/commands/hello.txt"), d), parse_mode="HTML")


@bot.message_handler(commands=['contact'])     #ответ на команду /contact - соо от бота + пересылка соо от пользователя создателям
def contact_message(message):
    bot.send_message(message.chat.id, texts("scenario/commands/contact.txt"))
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):             #надо всё-таки решить, что эта команда делает и кому сообщение отправляет (или записывает ответы пользователей?)
        bot.reply_to(message, 'Ваше сообщение доставлено!')
        bot.send_message(416671069, f'{message.text}, от {user(message)}; ID: {message.from_user.id}')

@bot.message_handler(commands=['newgame'])    #ответ на команду /newgame 
def newgame_message(message):
    conn = sqlite3.connect('tbdatabase.db')    #создание бд/подключение к бд, записывание пользователя, если его ещё нет
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id varchar(16) PRIMARY KEY, handler varchar(15))')
    cur.execute(f'INSERT INTO users (id, handler) VALUES ({message.from_user.id}, CURRENT_TIME) ON CONFLICT (id) DO UPDATE SET id = {message.from_user.id}, handler = CURRENT_TIME')
    conn.commit()
    cur.close()
    conn.close()

    i = 4
    for k in range(0,3):
        i -= 1
        bot.send_message(message.chat.id, str(i))
        time.sleep(1)
    bot.send_message(message.chat.id, "Поехали!")
    make_action(message, 1, False)

def make_action(message, n: int, NeedPhoto: bool):
    if n > 4:
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
        markup.add(types.InlineKeyboardButton(texts(f"scenario/lines_buttons/b{n}.txt"), callback_data="next"))
        bot.send_message(message.chat.id, texts(f"scenario/lines_direct/{n}.txt"), reply_markup=markup)


n = 1
@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):
    global n
    if callback.data == "next" and n < 5:
        n += 1
        if n in [2, 3, 4]:
            make_action(callback.message, n, True)
        else:
            make_action(callback.message, n, False)




bot.infinity_polling()
