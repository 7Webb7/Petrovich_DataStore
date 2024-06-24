import pandas as pd
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('Petrovich_Credentials.json', scope)
client = gspread.authorize(creds)


with open('venv/bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.read()

#iniini

try:
    df = pd.read_csv('petrovich_log.csv')
except:
    df = pd.DataFrame(columns=['Username', 'UserID', 'Message'])
    df.to_csv('petrovich_log.csv')
bot = telebot.TeleBot(token)

sheet_name = "Petrovich_Datasheet"
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/15M3Oc1t1eT84wOgPTMUX15kJWtP2e1y67lr16xNcLQ0/edit#gid=0'

try:
    spreadsheet = client.open_by_url(spreadsheet_url)
    sheet = spreadsheet.sheet1
    print(f"Found existing Google Sheet at '{spreadsheet_url}'.")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"Google Sheet at '{spreadsheet_url}' not found.")


sheet.update([df.columns.values.tolist()] + df.values.tolist())
spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
print(f'Data successfully written to {sheet_name}')
print(f'Google Sheet URL: {spreadsheet_url}')

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
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

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
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

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
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

@bot.message_handler(content_types=['text'])
def storing_handle(message):
    if message.text.startswith('/') and message.text in known_coms:
        return
    global df
    cut_df()
    df.loc[len(df.index)] = [message.from_user.username, message.from_user.id, message.text]
    df.to_csv('petrovich_log.csv', index=False)

    bot.reply_to(message, 'Сообщение записано.')
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

bot.polling(non_stop=True)
