import pandas as pd
import telebot
import datetime
import numpy as np
import recharge
with open('bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.read()


data = pd.read_csv('petrovich_log.csv')

df = pd.DataFrame(data)
known_commands = ['/start', '/messages', '/help']
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_handle(message):
    bot.send_message(message.chat.id, 'Привет, меня зовут Петрович. Нужно что?')
#@bot.message_handler(commands =['messages'])
#def print_messages(message):
@bot.message_handler(commands = ['messages'])
def handle_show_messages(message):
    unique_messages = {}
    for index, row in df[::-1].iterrows():
        if row['Message'] in unique_messages:
            continue
        unique_messages[row['Message']] = {'UserID': row['UserID'], 'Username': row['Username']}

        # Если набрали 10 уникальных сообщений, выходим из цикла
        if len(unique_messages) == 10:
            break
    for messages, user in unique_messages.items():
        bot.send_message(message.chat.id, f'Пользователь {user['Username']} (ID: {user['UserID']}) написал: "{messages}"')



@bot.message_handler(content_types= 'text')
def storing_handle(message):
    if message.text in known_commands:
        return
    global df

    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, message.text]
    df.to_csv('petrovich_log.csv', index=False)
    bot.reply_to(message, 'Сообщение записано.')


bot.polling(non_stop= True)



