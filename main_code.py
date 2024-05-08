import telebot

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


bot.infinity_polling()
