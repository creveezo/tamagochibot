import telebot
import sqlite3

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
        bot.send_message(message.from_user.id, 'Ваше сообщение доставлено!')
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


bot.infinity_polling()
