import pandas as pd
import telebot
import numpy as np

with open('bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.read()


data = pd.read_csv('petrovich_log.csv')

df = pd.DataFrame(data)
known_commands = ['/start', '/messages', '/help']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_handle(message):
    bot.send_message(message.chat.id, 'Привет, меня зовут Петрович. Нужно что?')


@bot.message_handler(commands = ['messages'])
def handle_show_messages(message):
    global df
    unique_messages = {}
    for index, row in df[::-1].iterrows():
        if row['Message'].startswith('/'):
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
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, '/messages']
    df.to_csv('petrovich_log.csv', index=False)

@bot.message_handler(commands = ['getcommands'])
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

    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, '/getcommands']
    df.to_csv('petrovich_log.csv', index=False)

@bot.message_handler(content_types= ['text', 'commands'])
def storing_handle(message):
    if message.text.startswith('/'):
        return
    global df

    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, message.text]
    df.to_csv('petrovich_log.csv', index=False)



    bot.reply_to(message, 'Сообщение записано.')


bot.polling(non_stop= True)



