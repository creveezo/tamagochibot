import telebot
from telebot import types
import sqlite3
import time
from decouple import config
from helpedit_funcs import *
from amusement_funcs import *
from feeding_funcs import *
from actionmaking_funcs import *
from checking_funcs import *


catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)


# ответ на команду /start
@bot.message_handler(commands=['start'])
def start_message(message):
    d = {"user": user(message)}
    bot.send_message(message.chat.id, format_replace(texts("commands/hello"), d), parse_mode="HTML")


# ответ на команду /menu
@bot.message_handler(commands=['menu'])
def menu_message(message):
    # сделать так чтобы человек не могу вызвать меню во время сюжета
    try:
        check = get_smth("training_complete", message.chat.id)
        if check == 0:
            bot.send_message(message.chat.id, "<i>Данная команда ещё не доступна</i>", parse_mode="HTML")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Покормить", callback_data="feed"))
            markup.add(types.InlineKeyboardButton("Развлечь", callback_data="funny"))

            bot.send_message(message.chat.id, 'Доступные действия:', reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, texts("action_responses/menuifdead"))


# ответ на команду /contact
# пересылка соо от пользователя создателям
@bot.message_handler(commands=['contact'])
def contact_message(message):
    bot.send_message(message.chat.id, texts("commands/contact"))

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        bot.reply_to(message, 'Ваше сообщение доставлено!')
        bot.send_message(416671069, f'{message.text}, от {user(message)}; ID: {message.from_user.id}')


# ответ на команду /newgame
@bot.message_handler(commands=['newgame'])
def newgame_message(message):

    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users \
                (id varchar(16) PRIMARY KEY, stage int, feedings_till_update int, action_number int, \
                kind_count_loc int, evil_count_loc int, cringe_count_loc int, \
                kind_count_abs int, evil_count_abs int, cringe_count_abs int, \
                lives int, fed_timestamp varchar(30), \
                temp1 varchar(50), temp2 varchar(50), temp_name varchar(200), \
                last_amuse_type varchar(10), amuse_timestamp varchar(30), stage_timestamp varchar(30), \
                training_complete int)')
    cur.execute('INSERT INTO users \
                (id, stage, feedings_till_update, action_number, \
                kind_count_loc, evil_count_loc, cringe_count_loc, \
                kind_count_abs, evil_count_abs, cringe_count_abs, \
                lives, fed_timestamp, \
                temp1, temp2, temp_name, \
                last_amuse_type, amuse_timestamp, stage_timestamp, \
                training_complete) \
                VALUES (?, 0, 2, 1, \
                0, 0, 0, \
                0, 0, 0, \
                3, 0, \
                0, 0, 0, \
                0, 0, 0, \
                0) \
                ON CONFLICT (id) DO UPDATE SET \
                id = ?, stage = 0, feedings_till_update = 2, action_number = 1, \
                kind_count_loc = 0, evil_count_loc = 0, cringe_count_loc = 0, \
                kind_count_abs = 0, evil_count_abs = 0, cringe_count_abs = 0, \
                lives = 3, fed_timestamp = 0, \
                temp1 = 0, temp2 = 0, temp_name = 0, \
                last_amuse_type = 0, amuse_timestamp = 0, stage_timestamp = 0, \
                training_complete = 0',
                (message.from_user.id, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()

    i = 4
    for _ in range(0, 3):    # обратный отсчет
        i -= 1
        bot.send_message(message.chat.id, str(i))
        time.sleep(1)
    bot.send_message(message.chat.id, "Поехали!")
    make_action(message, 1, False)


@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):

    if callback.data == "next":
        n = get_smth('action_number', callback.message.chat.id)

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=joiner(f'lines_direct/{n}', f'lines_buttons/b{n}'), parse_mode="HTML")
        n += 1
        push_smth('action_number', n, callback.message.chat.id)

        if n == 6:
            feed(callback.message.chat.id)
        if n in [2, 3, 4, 5, 6, 8]:
            if if_alive(callback.message.chat.id) == 1:
                make_action(callback.message, n, True)
        else:
            make_action(callback.message, n, False)

    if callback.data == "feed":
        c = feed(callback.message.chat.id)
        if c == 1:
            print('вот тут новый этап будет')
            # новый этап

    if callback.data == "funny":
        fun_choice(callback.message.chat.id)

    amusement = ["film", "book", "music", "youtube", "series", "cartoon", "game"]
    for amuse in amusement:
        if callback.data.find(amuse) != -1:
            push_smth("last_amuse_type", amuse, callback.message.chat.id)
            if callback.data == f"{amuse}_starting":
                amuse_time_push(callback.message.chat.id)
                response = texts(f'amusement/{callback.data}')
                bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                      text=joiner('lines_direct/6', f'amusement/{callback.data}_editor'))
                n = get_smth('action_number', callback.message.chat.id)
                n += 1
                push_smth('action_number', n, callback.message.chat.id)
                push_smth('temp1', response, callback.message.chat.id)
                make_action(callback.message, n, False)
            else:
                last_amusement = get_smth("last_amuse_type", callback.message.chat.id)
                if last_amusement == "film":
                    time = 3
                elif last_amusement == "youtube":
                    time = 2
                else:
                    time = 1.5
                if time_check("amuse", time, callback.message.chat.id) == 0:
                    bot.send_message(callback.message.chat.id,
                                     "Прошло недостаточно времени, пожалуйста, попробуйте позже.")
                else:
                    amusement_choice(amuse, callback.message)

    scale_types = ["kind", "cringe", "evil"]
    for scale in scale_types:
        if callback.data.find(scale) != -1:
            if callback.data == f"{scale}_starting":
                scale_count = get_smth(f'{scale}_count_loc', callback.message.chat.id)
                scale_count += 3
                push_smth(f'{scale}_count_loc', scale_count, callback.message.chat.id)
                n = get_smth('action_number', callback.message.chat.id)
                res = texts(f'temp/{callback.data}')
                bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                      text=joiner(texts('lines_direct/10'), invert(f'lines_buttons/c{n}')[callback.data], False))
                response = get_smth('temp1', callback.message.chat.id)
                bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')
                amuse_time_push(callback.message.chat.id)
                amuse = get_smth('last_amuse_type', callback.message.chat.id)
                amusement_choice(amuse, callback.message)
                n += 1
                push_smth('action_number', n, callback.message.chat.id)

            else:
                scale_count = get_smth(f'{scale}_count_loc', callback.message.chat.id)
                scale_count += int(callback.data[-1])
                push_smth(f'{scale}_count_loc', scale_count, callback.message.chat.id)
                if callback.data[-1] == "1":
                    amuse_time_push(callback.message.chat.id)
                    names = list(get_smth("temp_name", callback.message.chat.id).split("/"))
                    if scale == "kind":
                        curr_name = names[0]
                    elif scale == "cringe":
                        curr_name = names[1]
                    else:
                        curr_name = names[2]

                    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          text=joiner('Что у нас на сегодня?', curr_name, False))
                    n = get_smth("action_number", callback.message.chat.id)
                    amuse = get_smth('last_amuse_type', callback.message.chat.id)
                    if amuse == "film":
                        length = "3 часа"
                    elif amuse == "youtube":
                        length = "2 часа"
                    else:
                        length = "полтора часа"
                    bot.send_message(callback.message.chat.id, f"— Итак, теперь нам есть, на что потратить {length}...")
                    if n == 11:
                        make_action(callback.message, n, False)


bot.infinity_polling()