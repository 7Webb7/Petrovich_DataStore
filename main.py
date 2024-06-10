import pandas as pd
import telebot
import numpy as np

#запись в начале отдельной функцией, а в конце уже cuf_df


with open('venv/bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.read()

try:
    df = pd.read_csv('petrovich_log.csv')
except:
    df = pd.DataFrame(columns=['Username', 'UserID', 'Message'])
    df.to_csv('petrovich_log.csv')
bot = telebot.TeleBot(token)


def cut_df():  #перезапись при достижении лимита
    global df
    if len(df) > 300:
        df = df.iloc[-300:]


known_coms = ['/help', '/getcommands', '/messages', '/start']


@bot.message_handler(commands=['start'])
def start_handle(message):
    bot.send_message(message.chat.id, 'Привет, меня зовут Петрович. Нужно что?')


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id,
                     '/messages - получить список последних 10 уникальных сообщений \n /getcommands - получить список '
                     'последних использованных команд.')
    cut_df()
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, '/help']
    df.to_csv('petrovich_log.csv', index=False)


@bot.message_handler(commands=['messages'])
def handle_show_messages(message):
    global df
    unique_messages = {}
    for index, row in df[::-1].iterrows():
        if row['Message'].startswith('/') and row['Message'] in known_coms:
            continue
        if row['Message'] in unique_messages:
            continue
        unique_messages[row['Message']] = {'UserID': row['UserID'], 'Username': row['Username']}

        # Если набрали 10 уникальных сообщений, выходим из цикла
        if len(unique_messages) == 10:
            break
    message_string = ""
    for messages, user in unique_messages.items():
        message_string += f'Пользователь: {user['Username']}\t ID: {user['UserID']} \n\nСообщение: {messages} \n\n\n'
    bot.send_message(message.chat.id, message_string)
    cut_df()
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, '/messages']
    df.to_csv('petrovich_log.csv', index=False)


@bot.message_handler(commands=['counter'])
def give_counter(message):
    number_of_messages = len(df[df['UserID'] == message.from_user.id])
    user_status = ''
    if number_of_messages < 10:
        user_status = 'Слабовато.'
    if number_of_messages > 50:
        user_status = 'Вы - начинающий Петрович.'
    if number_of_messages > 200:
        user_status = 'Настоящий Петрович.'
    if number_of_messages > 800:
        user_status = 'Хватит спамить, Петрович.'

    bot.reply_to(message, f'Вы написали {number_of_messages} сообщений. {user_status}')


@bot.message_handler(commands=['getcommands'])
def handle_commands(message):
    global df
    commands = {}

    for index, row in df[::-1].iterrows():

        if not row['Message'].startswith('/'):
            continue

        commands[index] = {'UserID': row['UserID'], 'Username': row['Username'], 'Message': row['Message']}

        # Если набрали 10 уникальных сообщений, выходим из цикла
        if len(commands) == 10:
            break
    message_string = ""
    for messages, user in commands.items():
        message_string += f'Пользователь: {user['Username']}\t ID: {user['UserID']} \n\nИспользовал: {user['Message']} \n\n\n'
    bot.send_message(message.chat.id, message_string)
    cut_df()
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, '/getcommands']
    df.to_csv('petrovich_log.csv', index=False)


@bot.message_handler(content_types=['text'])
def storing_handle(message):
    if message.text.startswith('/') and message.text in known_coms:
        return
    global df
    cut_df()
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, message.text]
    df.to_csv('petrovich_log.csv', index=False)

    bot.reply_to(message, 'Сообщение записано.')


bot.polling(non_stop=True)
