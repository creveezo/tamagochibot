import telebot
from telebot import types

token = "6968907461:AAG5j6gXd2B5WAsCL6jDC8_85I4YzskXUKg"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['choices'])
def probnik(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Фильм!', callback_data='a')
    button2 = types.InlineKeyboardButton(text='Музыка!', callback_data='b')
    button3 = types.InlineKeyboardButton(text='Книжки!', callback_data='c')
    markup.row(button1, button2, button3)

    bot.send_message(message.chat.id, "Пора эту тварь развлечь.", reply_markup=markup)


def RazlitPivo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Поменять воду', callback_data='x'))
    markup.add(types.InlineKeyboardButton('Оставить', callback_data='y'))
    markup.add(types.InlineKeyboardButton('Долить', callback_data='z'))

    bot.send_message(message.chat.id, 'ай!!! разлили пиво!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):
    global response
    if callback.data in ['a', 'b', 'c']:
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Пора эту тварь развлечь.\n\n(Ты что-то сделал)')
        bot.send_message(callback.message.chat.id, 'балдеж, но сначала за пивом.')
        RazlitPivo(callback.message)
    if callback.data == 'a':
        response = 'глянем. Господи, куда тебе показывать-то...'
    if callback.data == 'b':
        response = 'послушаем.'
    if callback.data == 'c':
        response = 'почитаем.'
    if callback.data == 'x':
        res = 'Надеюсь, что обошлось.'
        bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')
    if callback.data == 'y':
        res = 'И так сойдёт.'
        bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')
    if callback.data == 'z':
        res = 'В целом, ему нужнее.'
        bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')


bot.infinity_polling()
