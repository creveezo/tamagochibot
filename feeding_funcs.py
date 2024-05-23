import telebot
import sqlite3
from datetime import datetime
from decouple import config
from helpedit_funcs import get_smth, push_smth, texts


catgirl = config('CATGIRL')
normal = config('NORMAL')
bot = telebot.TeleBot(catgirl)


# кормление
def feed(id):
    fed = get_smth('fed_timestamp', id)
    trcheck = get_smth('training_complete', id)
    ifupgrade = 0    # переходим ли на следующий этап

    if trcheck == 0:
        fcheck = 'NO'

    if trcheck == 1:
        fcheck = fed_check(fed, id)

    if fcheck == 'NO':
        count = get_smth('feedings_till_update', id)
        count -= 1
        if count == 0:
            count = update_stage(id)
            ifupgrade = 1
        if ifupgrade == 0:
            bot.send_message(id, texts("action_responses/fed"))
            fednow = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            push_smth('fed_timestamp', fednow, id)
        push_smth('feedings_till_update', count, id)
        
    if fcheck == 'YES':
        bot.send_message(id, texts("action_responses/cant_feed"))

    if fcheck == 'DEATH':
        conn = sqlite3.connect('tbdatabase.db')
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        cur.close()
        conn.close()

    return ifupgrade


# апдейт стадии - перед началом следующего этапа проверять
# с помощью time_check(), что прошло 12 часов с stage_timestamp
def update_stage(id):
    stage = get_smth('stage', id)
    stage += 1
    if stage == 1:
        count = 3
    elif stage == 4:
        count = 0
    elif stage == 2 or stage == 3:
        count = 4
    push_smth('stage', stage, id)
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    push_smth('stage_timestamp', time, id)
    push_smth('action_number', 1, id)
    for scale in ['kind', 'cringe', 'evil']:
        scale_loc = get_smth(f'{scale}_count_loc', id)
        scale_abs = get_smth(f'{scale}_count_abs', id)
        scale_abs += scale_loc
        push_smth(f'{scale}_count_abs', scale_abs, id)
        push_smth(f'{scale}_count_loc', 0, id)
    return count


# проверка накормленности и пропусков
def fed_check(fed, id):
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
            bot.send_message(id, texts("action_responses/2tilld"))
        elif lives == 1:
            bot.send_message(id, texts("action_responses/1tilld"))
        elif lives == 0:
            bot.send_message(id, texts("action_responses/d"))
            fcheck = 'DEATH'
        push_smth('lives', lives, id)
    return fcheck


# проверка, прошло ли time часов с момента в amuse_timestamp и stage_timestamp
# time пишите в часах пожалуйста. category - либо amuse, либо stage
def time_check(category, time, id):
    time = time * 60*60
    curr = datetime.now()
    did = get_smth(f'{category}_timestamp', id)
    did = datetime.strptime(did[:19], '%Y-%m-%d %H:%M:%S')
    diff = curr - did
    diffsec = diff.seconds + diff.days * 60*60*24
    if diffsec > time:
        ans = 1
    else:
        ans = 0
    return ans