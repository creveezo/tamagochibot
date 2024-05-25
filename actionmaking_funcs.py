import telebot
from telebot import types
import time
from telebot.types import InputFile
from decouple import config
from helpedit_funcs import push_smth, texts, choice


catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)


# считывает линейные действия
def make_action(message, n: int, NeedPhoto: bool):
    if n == 10:
        bot.send_message(message.chat.id, texts("lines_direct/10_1"), parse_mode="HTML")
    if n == 11:
        push_smth("training_complete", 1, message.chat.id)
    if n in [6, 10]:
        return choice(message, n)
    if n > 12:
        bot.send_message(message.chat.id, "<i>кто прочитал тот сдох...(с вас 5 рублей)</i>", parse_mode="HTML")
    else:
        if n == 4:
            bot.send_message(message.chat.id, "Ну, конечно. На обратной стороне было неприлично много писанины:")
            # time.sleep(2)
        if NeedPhoto:
            try:
                photo = open(f'scenario/photos/{n}.png', 'rb')
                bot.send_photo(message.chat.id, photo)
            except Exception:
                bot.send_animation(message.chat.id, InputFile(f'scenario/photos/{n}.mp4'))

            if n == 4:
                bot.send_message(message.chat.id, texts("lines_direct/4_1"))

            # time.sleep(5)
        markup = types.InlineKeyboardMarkup()
        if n != 12:
            markup.add(types.InlineKeyboardButton(texts(f"lines_buttons/b{n}"), callback_data="next"))
        bot.send_message(message.chat.id, texts(f"lines_direct/{n}"), reply_markup=markup, parse_mode="HTML")