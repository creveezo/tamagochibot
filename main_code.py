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
    cur.execute('CREATE TABLE IF NOT EXISTS users \
                (id varchar(16) PRIMARY KEY, stage int, feedings_till_update int, action_number int, \
                good_count_loc int, evil_count_loc int, cringe_count_loc int, \
                good_count_abs int, evil_count_abs int, cringe_count_abs int, \
                lives int, already_fed int, \
                temp1 varchar(50), temp2 varchar(50), training_complete int)')
    cur.execute('INSERT INTO users \
                (id, stage, feedings_till_update, action_number, \
                good_count_loc, evil_count_loc, cringe_count_loc, \
                good_count_abs, evil_count_abs, cringe_count_abs, \
                lives, already_fed, \
                temp1, temp2, training_complete) \
                VALUES (?, 0, 2, 1, \
                0, 0, 0, 0, 0, 0, \
                3, 0, 0, 0, 0) \
                ON CONFLICT (id) DO UPDATE SET \
                id = ?, stage = 0, feedings_till_update = 2, action_number = 1, \
                good_count_loc = 0, evil_count_loc = 0, cringe_count_loc = 0, \
                good_count_abs = 0, evil_count_abs = 0, cringe_count_abs = 0, \
                lives = 3, already_fed = 0, \
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
        bot.send_message(message.chat.id, texts("lines_direct/10_1.txt"))
    # надо не забыть присылать фоту если мы делаем ретерн чойс как у действия 6
    if n in [6, 10]:
        return choice(message, n)
    if n > 10:
        bot.send_message(message.chat.id, "<i>кто прочитал тот сдох...(с вас 5 рублей)</i>", parse_mode="HTML")
    else:
        if n == 4:
            bot.send_message(message.chat.id, "Ну конечно. На обратной стороне было неприлично много писанины:")
            #time.sleep(2)
        if NeedPhoto:
            photo = open(f'scenario/photos/{n}.png', 'rb')
            bot.send_photo(message.chat.id, photo)
            #time.sleep(5)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(texts(f"lines_buttons/b{n}.txt"), callback_data="next"))
        bot.send_message(message.chat.id, texts(f"lines_direct/{n}.txt"), reply_markup=markup)


def choice(message, n):
    markup = types.InlineKeyboardMarkup()
    for var, cb in texts(f"lines_buttons/c{n}.txt").items():
        markup.add(types.InlineKeyboardButton(str(var), callback_data=cb))
    bot.send_message(message.chat.id, texts(f"lines_direct/{n}.txt"), reply_markup=markup)


def get_smth(column, id):   #достать значение из бд
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

def feed(id):   #кормление + сделать взаимодействие с already_fed (внутри или снаружи функции) так, чтобы он прибавлялся и убирал возможность кормить в этот промежуток времени
    count = get_smth('feedings_till_update', id)
    count -= 1
    if count == 0:
        count = update_stage(id)
    push_smth('feedings_till_update', count, id)

def update_stage(id):   #апдейт стадии
    stage = get_smth('stage', id)
    if stage == 0:
        count = 3
    if stage == 1 or 2:
        count = 4
    if stage == 3:
        count = 0
    stage += 1
    push_smth('stage', stage, id)
    return count

def fed_check():    #проверка накормленности и предупреждение + сделать запуск в определенное время + сделать смерть существа и тексты предупреждений
    fed = get_smth('already_fed', id)
    if fed == 1:
        push_smth('already_fed', 0, id)
    if fed == 0:
            lives = get_smth('lives', id)
            lives -= 1
            if lives == 2:
                print('2 till wasted')
            if lives == 1:
                print('1 till wasted')
            if lives == 0:
                print('wasted')
            push_smth('lives', lives, id)
            

@bot.callback_query_handler(func=lambda callback: True)
def buttons_callback(callback):

    if callback.data == "next":
        n = get_smth('action_number', callback.message.chat.id)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=joiner((f'lines_direct/{n}.txt'), (f'lines_buttons/b{n}.txt')))
        
        n += 1
        push_smth('action_number', n, callback.message.chat.id)

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
        n = get_smth('action_number', callback.message.chat.id)
        n += 1
        push_smth('action_number', n, callback.message.chat.id)
        push_smth('temp1', response, callback.message.chat.id)
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
        response = get_smth('temp1', callback.message.chat.id)
        bot.send_message(callback.message.chat.id, f'{res} Ну, малявка, давай что-нибудь {response}')
        n = get_smth('action_number', callback.message.chat.id)
        n += 1
        push_smth('action_number', n, callback.message.chat.id)
        make_action(callback.message, n, False)


bot.infinity_polling()
