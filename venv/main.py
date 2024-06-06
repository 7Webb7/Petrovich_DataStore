import pandas as pd
import telebot
import datetime

with open('bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.read()

data = pd.read_csv('petrovich_log.csv')
df = pd.DataFrame(data)

bot = telebot.TeleBot(token)
@bot.message_handler(commands=['/start'])
def start_handle(message):
    bot.send_message(message.chat.id, 'Привет, меня зовут Петрович. Нужно что?')
@bot.message_handler(content_types= 'text')
def storing_handle(message):
    global df
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.loc[len(df.index)] = [message.from_user.id, timestamp, message.message_id, message.text]
    df.to_csv('petrovich_log.csv', index=False)
    bot.reply_to(message, 'Сообщение записано.')

bot.polling(non_stop= True)



