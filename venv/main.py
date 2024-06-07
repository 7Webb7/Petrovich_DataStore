import pandas as pd
import telebot
import datetime
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
@bot.message_handler(commands =['messages'])
def print_messages(message):
    to_print = np.array(df.loc[:, ['Message']])
    to_print = np.unique(to_print)[-10:]

    for i in range(len(to_print)):

        bot.send_message(message.chat.id, f"{i+1}. {to_print[i]}")

@bot.message_handler(content_types= 'text')
def storing_handle(message):
    if message.text in known_commands:
        return
    global df
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.loc[len(df.index)] = [message.from_user.id, timestamp, message.message_id, message.text]
    df.to_csv('petrovich_log.csv', index=False)
    bot.reply_to(message, 'Сообщение записано.')

bot.polling(non_stop= True)



