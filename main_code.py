import telebot
from telebot import types
import sqlite3
import time
import random
from datetime import datetime

catgirl = '6968907461:AAG5j6gXd2B5WAsCL6jDC8_85I4YzskXUKg'
normal = '6595427590:AAEWir1FTJpltWi2B1SIbBokhs7rSRSe7Rk'
bot = telebot.TeleBot(catgirl)

def user(message):  # получаем имя пользователя
    return " ".join(filter(lambda x:x, [message.from_user.first_name, message.from_user.last_name]))


def texts(file: str):        # достаём текст из файла, если есть выборы то делаем словарь {текст кнопки: колбек данные}
    if file.find('lines_buttons/c') != -1:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            l = file.read().split("\n")
            d = {}
            for line in l:
                button_text, cb = line.split(";")
                d[button_text] = cb
            return d
    else:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            return file.read()


def invert(file):
    if str(file).find('lines_buttons/c') != -1:
        with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
            l = file.read().split("\n")
            d = {}
            for line in l:
                button_text, cb = line.split(";")
                d[cb] = button_text
            return d



def joiner(text1, text2, NeedTexts=True) -> str:       # функция для редактирования сообщений (два фрагмента текста совмещает в один)
    if NeedTexts == False:
        return f'{text1}\n\n{text2}'
    return f"{texts(text1)}\n\n{texts(text2)}"

def format_replace(line, d):
    for key, value in d.items():
        line = line.replace("{" + key + "}", value)
    return line


def randomiser(file):
    with open(f"scenario/{file}.txt", "r", encoding="UTF-8") as file:
        list = file.read().split("\n")
        return random.choice(list)


def amusement_choice(type):
    kind = randomiser(f'{type}_kind')
    cringe = randomiser(f'{type}_cringe')
    evil = randomiser(f'{type}_evil')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(kind, callback_data="kind_1"))
    markup.add(types.InlineKeyboardButton(cringe, callback_data="cringe_1"))
    markup.add(types.InlineKeyboardButton(evil, callback_data="evil_1"))

    #bot.send_message(chat.id, 'Что у нас на сегодня?', reply_markup=markup)










@bot.message_handler(commands=['start'])  # ответ на команду /start - соо от бота
def start_message(message):
    d = {"user": user(message)}
    bot.send_message(message.chat.id, format_replace(texts("commands/hello"), d), parse_mode="HTML")


@bot.message_handler(commands=['contact'])     #ответ на команду /contact - соо от бота + пересылка соо от пользователя создателям
def contact_message(message):
    bot.send_message(message.chat.id, texts("commands/contact"))
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):             #надо всё-таки решить, что эта команда делает и кому сообщение отправляет (или записывает ответы пользователей?)
        bot.reply_to(message, 'Ваше сообщение доставлено!')
        bot.send_message(416671069, f'{message.text}, от {user(message)}; ID: {message.from_user.id}')

@bot.message_handler(commands=['newgame'])    #ответ на команду /newgame 
def newgame_message(message):

    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users \
                (id varchar(16) PRIMARY KEY, stage int, feedings_till_update int, action_number int, \
                kind_count_loc int, evil_count_loc int, cringe_count_loc int, \
                kind_count_abs int, evil_count_abs int, cringe_count_abs int, \
                lives int, fed_timestamp varchar(30), \
                temp1 varchar(50), temp2 varchar(50), training_complete int)')
    cur.execute('INSERT INTO users \
                (id, stage, feedings_till_update, action_number, \
                kind_count_loc, evil_count_loc, cringe_count_loc, \
                kind_count_abs, evil_count_abs, cringe_count_abs, \
                lives, fed_timestamp, \
                temp1, temp2, training_complete) \
                VALUES (?, 0, 2, 1, \
                0, 0, 0, \
                0, 0, 0, \
                3, 0, \
                0, 0, 0) \
                ON CONFLICT (id) DO UPDATE SET \
                id = ?, stage = 0, feedings_till_update = 2, action_number = 1, \
                kind_count_loc = 0, evil_count_loc = 0, cringe_count_loc = 0, \
                kind_count_abs = 0, evil_count_abs = 0, cringe_count_abs = 0, \
                lives = 3, fed_timestamp = 0, \
                temp1 = 0, temp2 = 0, training_complete = 0', \
                (message.from_user.id, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()

    i = 4
    for k in range(0,3):    # обратный отсчет
        i -= 1
        bot.send_message(message.chat.id, str(i))
        #time.sleep(1)
    bot.send_message(message.chat.id, "Поехали!")
    make_action(message, 1, False)


def make_action(message, n: int, NeedPhoto: bool):    # считывает линейные действия
    if n == 10:
        bot.send_message(message.chat.id, texts("lines_direct/10_1"), parse_mode="HTML")
    # надо не забыть присылать фоту если мы делаем ретерн чойс как у действия 6
    if n in [6, 10]:
        return choice(message, n)
    if n > 10:
        bot.send_message(message.chat.id, "<i>кто прочитал тот сдох...(с вас 5 рублей)</i>", parse_mode="HTML")
    else:
        if n == 4:
            bot.send_message(message.chat.id, "Ну, конечно. На обратной стороне было неприлично много писанины:")
            #time.sleep(2)
        if NeedPhoto:
            try:
                photo = open(f'scenario/photos/{n}.png', 'rb')
                bot.send_photo(message.chat.id, photo)
            except:
                gif = open(f'scenario/photos/{n}.gif', 'rb')
                bot.send_document(message.chat.id, gif)


            if n == 4:
                bot.send_message(message.chat.id, texts("lines_direct/4_1"))

            #time.sleep(5)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(texts(f"lines_buttons/b{n}"), callback_data="next"))
        bot.send_message(message.chat.id, texts(f"lines_direct/{n}"), reply_markup=markup)


def choice(message, n):
    markup = types.InlineKeyboardMarkup()
    for var, cb in texts(f"lines_buttons/c{n}").items():
        markup.add(types.InlineKeyboardButton(str(var), callback_data=cb))
    bot.send_message(message.chat.id, texts(f"lines_direct/{n}"), reply_markup=markup)


def get_smth(column, id):   # достать значение из бд
    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute(f'SELECT {column} FROM users WHERE id = ?', (id,))
    value = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return value

def push_smth(column, value, id):   #записать значение в бд
    conn = sqlite3.connect('tbdatabase.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET {column} = ? WHERE id = ?', (value, id))
    conn.commit()
    cur.close()
    conn.close()

def feed(id):   # кормление
    fed = get_smth('fed_timestamp', id)
    trcheck = get_smth('training_complete', id)
    if trcheck == 0:
        fcheck = 'NO'
    if trcheck == 1:
        fcheck = fed_check(fed, id)
    if fcheck == 'NO':
        count = get_smth('feedings_till_update', id)
        count -= 1
        if count == 0:
            count = update_stage(id)
        fednow = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        push_smth('fed_timestamp', fednow, id)
        push_smth('feedings_till_update', count, id)
        print('спасибо что покормили')
    if fcheck == 'YES':
        print('покормили уже')
    if fcheck == 'DEATH':
        conn = sqlite3.connect('tbdatabase.db')
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        cur.close()
        conn.close()
        #сделать чтобы потом на кнопочки нельзя было тыкать
        


def update_stage(id):   # апдейт стадии
    stage = get_smth('stage', id)
    stage += 1
    if stage == 1:
        count = 3
    elif stage == 4:
        count = 0
    elif stage == 2 or stage == 3:
        count = 4
    push_smth('stage', stage, id)
    push_smth('action_number', 1, id)
    for scale in ['kind', 'cringe', 'evil']:
        scale_loc = get_smth(f'{scale}_count_loc', id)
        scale_abs = get_smth(f'{scale}_count_abs', id)
        scale_abs += scale_loc
        push_smth(f'{scale}_count_abs', scale_abs, id)
        push_smth(f'{scale}_count_loc', 0, id)
    return count


def fed_check(fed, id):    # проверка накормленности и пропусков
    curr = datetime.now()
    fed = datetime.strptime(fed[:19], '%Y-%m-%d %H:%M:%S')
    diff = curr - fed
    diffsec = diff.seconds + diff.days * 60*60*24
    if diffsec <= 43200:
        fcheck = 'YES'
    if diffsec > 43200:
        fcheck = 'NO'
    if diffsec > 86400:
        lives = get_smth('lives', id)
        lives -= 1
        if lives == 2:
            print('2 till death')
        elif lives == 1:
            print('1 till death')
        elif lives == 0:
            print('death')
            fcheck = 'DEATH'
        push_smth('lives', lives, id)
    return fcheck



@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):

    if callback.data == "next":
        n = get_smth('action_number', callback.message.chat.id)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=joiner(f'lines_direct/{n}', f'lines_buttons/b{n}'))
        n += 1
        push_smth('action_number', n, callback.message.chat.id)

        if n in [2, 3, 4, 5, 6, 8]:
            make_action(callback.message, n, True)
        if n == 6:
            feed(callback.message.chat.id)
        else:
            make_action(callback.message, n, False)

    amusement = ["film", "book", "music"]
    for amuse in amusement:
        if callback.data.find(amuse) != -1:
            if callback.data == f"{amuse}_starting":
                response = texts(f'amusement/{callback.data}')
                bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                      text=joiner('lines_direct/6', f'amusement/{callback.data}_editor'))
                n = get_smth('action_number', callback.message.chat.id)
                n += 1
                push_smth('action_number', n, callback.message.chat.id)
                push_smth('temp1', response, callback.message.chat.id)
                push_smth('temp2', amuse, callback.message.chat.id)
                make_action(callback.message, n, False)


    scale_types = ["kind", "cringe", "evil"]
    for scale in scale_types:
        if callback.data.find(scale) != -1:
            if callback.data == f"{scale}_starting":
                n = get_smth('action_number', callback.message.chat.id)
                res = texts(f'temp/{callback.data}')
                bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                      text=joiner(texts('lines_direct/10'), invert(f'lines_buttons/c{n}')[callback.data], False))
                response = get_smth('temp1', callback.message.chat.id)
                bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')


                n += 1
                push_smth('action_number', n, callback.message.chat.id)
                make_action(callback.message, n, False)
                bot.send_message(callback.message.chat.id, "тут будет выбор из трех но пока его нет но он будет")
                amuse = get_smth('temp2', callback.message.chat.id)
                if amuse == "film":
                    lenth = "3 часа"
                elif amuse == "youtube":
                    lenth = "2 часа"
                else:
                    lenth = "полтора часа"
                bot.send_message(callback.message.chat.id, f"— Итак, теперь нам есть, на что потратить {lenth}...")
            else:
                scale_count = get_smth(f'{scale}_count_loc', callback.message.chat.id)
                scale_count += callback.data[-1]
                push_smth(f'{scale}_count_loc', scale_count, callback.message.chat.id)


bot.infinity_polling()
