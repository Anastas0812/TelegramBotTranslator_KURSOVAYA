import random
import telebot
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import psycopg2
import configparser
import DataBase

config = configparser.ConfigParser()
config.read('settings.ini')
password = config['Postgres']['password']
TOKEN = config['TELEGRAM']['TOKEN']

"""Global variables."""
unique_id_user = None
rus_delete = None
rus_w_from_db = None
rus_add = None
eng_add = None

print('Bot is working...')

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    """concatenate list items into one line, starting on a new line"""
    return '\n'.join(lines)

def show_en(data):
    """response template"""
    return f"{data['en']} -> {data['translate_word']}"

class Command:
    """ button name """
    ADD_WORD = 'Добавить слово ✍️'
    DELETE_WORD = 'Удалить слово✖️'
    NEXT = 'Дальше ➡️'

class MyStates(StatesGroup):
    """A class representing similar states"""
    en = State()
    translate_word = State()
    another_words = State()

@bot.message_handler(commands=['start', 'tasks'])
def send_welcome(message):
    """starting the bot
    if we don’t know the user yet, then we create a personal table for him (personal_table_OFU).
    Copy Russian and English words from the main table, then update the data in id
    create buttons and assign them appropriate content
    """
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    global unique_id_user
    unique_id_user = message.chat.id
    if unique_id_user not in known_users:
        known_users.append(unique_id_user)
        userStep[unique_id_user] = 0
        bot.send_message(unique_id_user, 'Привет, мой будущий полиглот! 😜')
        bot.send_message(unique_id_user, f'Приступим?')
        cur.execute(f'CREATE TABLE IF NOT EXISTS personal_table_OFU (id VARCHAR(100), russian_word VARCHAR(100), english_word VARCHAR(100));')
        conn.commit()
        cur.execute("INSERT INTO personal_table_OFU SELECT id, russian_word, english_word FROM main_table1;")
        conn.commit()
        cur.execute(f"UPDATE personal_table_OFU SET id = {unique_id_user};")
        conn.commit()
        cur.close()
        conn.close()

    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    cur.execute('SELECT russian_word FROM personal_table_OFU;')
    r = cur.fetchall()
    cur.execute('SELECT english_word FROM personal_table_OFU;')
    e = cur.fetchall()
    cur.close()
    conn.close()
    global rus_w_from_db
    rus_w_from_db = [str(item) for sub in r for item in sub]
    eng_w_from_db = [str(item) for sub in e for item in sub]
    for r, e in zip(rus_w_from_db, eng_w_from_db):
        rus = r
        en = e
    rus = random.choice(rus_w_from_db)
    index_rus = rus_w_from_db.index(rus)
    index_en = eng_w_from_db[index_rus]
    if rus:
        en = index_en

    en_btn = types.KeyboardButton(en)
    buttons.append(en_btn)
    other_w = []
    for word in range(4):
        try:
            if en != eng_w_from_db[word]:
                other_w.append(eng_w_from_db[word])
        except:
            print('Ого, похоже у нас тут английские омонимы!')
    other_w_btn = [types.KeyboardButton(word) for word in other_w]
    buttons.extend(other_w_btn)
    random.shuffle(buttons)
    random.shuffle(other_w)

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])
    markup.add(*buttons)

    greeting = f'Переведи слово:\n{rus}'
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.en, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['en'] = en
        data['translate_word'] = rus
        data['other_words'] = other_w

with open('help_user.txt') as f:
    """first write the text that will be displayed when you select the /help command"""
    data = f.read()

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, f'{data}')

@bot.message_handler(commands=['new_words'])
def get_new_words(message):
    """additional feature. we will help the user display the number of added words"""
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    cur.execute('SELECT * FROM new_words_OFU;')
    bot.send_message(message.chat.id, f'Вот сколько новых слов было добавлено тобой: {len(cur.fetchall())}.')
    cur.close()
    conn.close()

@bot.message_handler(commands=['deleted_words'])
def get_deleted_words(message):
    """additional feature. we will help the user display the number of deleted words"""
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    cur.execute('SELECT * FROM deleted_words_OFU;')
    bot.send_message(message.chat.id, f'Количество слов, которые ты удалил: {len(cur.fetchall())}.')
    cur.close()
    conn.close()


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_tasks(message):
    """button 'NEXT' setting"""
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    """button 'DELETE_WORD' setting"""
    bot.reply_to(message, 'Окей, дружище 👌. Напиши (на русском), какое слово удалить')
    bot.register_next_step_handler(message, delete_input)
def delete_input(message):
    global rus_delete
    rus_delete = message.text.lower()
    if rus_delete in rus_w_from_db:
        bot.reply_to(message, f'Слово "{rus_delete}" удалено 😿')
        conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
        cur = conn.cursor()
        cur.execute("INSERT INTO deleted_words_OFU (id, russian_word, english_word) VALUES ('%s', '%s', '%s')" % (unique_id_user, rus_delete, 'null'))
        conn.commit()
        cur.execute("DELETE FROM personal_table_OFU WHERE russian_word = ('%s');" % (rus_delete))
        conn.commit()
        cur.close()
        conn.close()
    else:
        bot.reply_to(message, f'Кажется, такое слово мы с тобой не изучали 🤨')


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    """button 'ADD_WORD' setting"""
    unique_id_user = message.chat.id
    userStep[unique_id_user] = 1
    msg = bot.send_message(message.chat.id, 'Похвально, давай пополним словарь 💪. Напиши слово на русском')
    bot.register_next_step_handler(msg, russian_input)

def russian_input(message):
    global rus_add
    rus_add = message.text.lower()
    bot.reply_to(message, f'Отлично, слово "{message.text}" добавлено 🤌. Напиши перевод этого слова на английском')
    bot.register_next_step_handler(message, english_input)

def english_input(message):
    global eng_add
    eng_add = message.text.lower()
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    cur.execute("INSERT INTO new_words_OFU (id, russian_word, english_word) VALUES ('%s', '%s', '%s');" % (unique_id_user, rus_add, eng_add))
    conn.commit()
    cur.execute(
        "INSERT INTO personal_table_OFU (id, russian_word, english_word) VALUES ('%s', '%s', '%s');" % (unique_id_user, rus_add, eng_add))
    conn.commit()
    bot.reply_to(message, f'Новое слово успешно добавлено 🫡\n{rus_add}-->{eng_add}')
    conn = psycopg2.connect(database='dict_rus_en', user='postgres', password=password)
    cur = conn.cursor()
    cur.execute('SELECT * FROM personal_table_OFU;')
    res_personal = len(cur.fetchall())
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Ого, дружище! Ты изучаешь уже {res_personal} слов(а) 😎')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    """bot, recognize and process incoming text"""
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        en = data['en']
        if text == en:
            hint = show_en(data)
            hint_text = ['Прекрасно!', hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)




