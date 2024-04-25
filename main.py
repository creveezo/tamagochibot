import telebot


token = "6968907461:AAG5j6gXd2B5WAsCL6jDC8_85I4YzskXUKg"
def user(message):    #получаем имя пользователя
    if message.from_user.last_name == None:
        return message.from_user.first_name
    return f"{message.from_user.first_name} {message.from_user.last_name}"
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])    #ответ на команду /start - соо от бота
def start_message(message):
    bot.send_message(message.chat.id, f"<i>Привет, {user(message)}!</i>"
                                      "\n\nС сегодняшнего дня ты станешь частью невероятного научного эксперимента, "
                                      "подробности о котором, впрочем, узнаешь немного позже 🧪 "
                                      "Тебе предстоит решить судьбу всего… <tg-spoiler>лишь одного небольшого существа, зато какого</tg-spoiler>! "
                                      "Совсем скоро ты познакомишься с многочисленными деталями и тонкостями такого непростого дела, "
                                      "а пока — welcome to <b>Название игры</b>! 🫧"
                                      "\n\nНабор <s>химикатов</s> команд, которые могут понадобиться в течение прохождения:"
                                      "\n\n/newgame - начинается новая игровая сессия"
                                      "\n❗️ важно: если игровая сессия уже начата, при вызове этой команды весь прогресс обнулится ❗️"
                                      "\n/start - появится то же сообщение, что ты читаешь прямо сейчас 👀"
                                      "\n/contact - через эту команду можно написать нам, создателям игры! Мы всегда ждем отзывов и предложений 🤍"
                                      "\n\n<i>И помни: каждое твое действие имеет последствия…</i>", parse_mode="HTML")

@bot.message_handler(commands=['newgame'])    #ответ на команду /newgame - соо от бота с кнопками
def newgame_message(message):
    bot.send_message(message.chat.id, '*тут было вступление написанное леной но я его случайно удалила. Потом верну*') #вернуть описание и добавить кнопки!!!!!!
@bot.message_handler(commands=['ab'])    #ответ на команду /ab - соо от бота
def ab_message(message):
    bot.send_message(message.chat.id, message) #потом удалить обязательно эту команду
@bot.message_handler(commands=['contact'])    #ответ на команду /contact - соо от бота + пересылка соо от пользователя создателям
def contact_message(message):
    bot.send_message(message.chat.id, "Если вы хотите поделиться вашими пожеланиями, впечатлениями или предложениями, пожалуйста, напишите их! (следующее ваше одно сообщение будет направлено одному из команды создателей)")
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        bot.send_message(message.from_user.id, 'Ваше сообщение доставлено!')
        bot.send_message(416671069, f'{message.text}, от {user(message)}; ID: {message.from_user.id}')

bot.infinity_polling()
