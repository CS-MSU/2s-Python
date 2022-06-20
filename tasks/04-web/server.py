import os
import time

import yaml
import requests

from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from subprocess import Popen, PIPE
from flask import Flask, request, abort


def logger(message):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    os.system(f'echo LOGGER:\t{cur_time}\t{message}')


def run_ngrok():
    logger("Starting Ngrok service")
    _ = Popen(['ngrok', 'http', str(PORT)], stdout=PIPE)
    logger(f"Waiting 10 seconds")
    time.sleep(10)
    url = None
    try:
        response = requests.get('http://localhost:4040/api/tunnels').json()
        url = response['tunnels'][0]['public_url']
        logger(f"Ngrok url: {url}")
    except Exception as e:
        logger(f"Cant get Ngrok URL with message: {e}")
    return url


with open("config.yml", "r") as f:
    os.system(f'echo ')
    config = yaml.load(f, yaml.Loader)

TOKEN = config.get('bot').get('token')
HOST = config.get('api').get('host')
PORT = config.get('api').get('port')
DEBUG = config.get('debug')


bot = TeleBot(TOKEN)
app = Flask(__name__)

other_types = [
    'text', 'audio', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact', 'new_chat_members',
    'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created',
    'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message', 'left_chat_member'
]
users = {}


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Отправить изображение обратно", callback_data="send_back"))
    return markup


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if DEBUG:
        logger(f"User: {chat_id}\tStart using bot")
    users[chat_id] = {}
    bot.send_message(chat_id, 'Привет, я бот, который может обрабатывать только изображения в формате jpg и png')


@bot.message_handler(func=lambda message: True, content_types=other_types)
def other_message(message):
    chat_id = message.chat.id
    if chat_id in users:
        if DEBUG:
            logger(f"User: {chat_id}\tОтправил сообщение в не правильном формате")
        bot.send_message(chat_id, 'Не верный формат. Нужно отправить изображение в формате jpg и png')
    else:
        bot.send_message(chat_id, 'Сначала вы должны стартовать бот коммандой /start')


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def photo_message(message):
    chat_id = message.chat.id
    if chat_id in users:
        users[chat_id]['img'] = None
        users[chat_id]['type'] = None
        if message is not None and message.photo is not None and len(message.photo) and message.photo[0].file_id is not None:
            if DEBUG:
                logger(f"User: {chat_id}\tОтправил изображение")
            users[chat_id]['img'] = message.photo[0].file_id
            users[chat_id]['type'] = 'photo'
            bot.send_message(chat_id, 'Нажмите кнопку или отправьте новое изображение', reply_markup=gen_markup())
        else:
            if DEBUG:
                logger(f"User: {chat_id}\tОтправил изображение в не правильном формате")
            bot.send_message(chat_id, 'Не верный формат. Нужно отправить изображение в формате jpg и png')
    else:
        bot.send_message(chat_id, 'Сначала вы должны стартовать бот коммандой /start')


@bot.message_handler(func=lambda message: True, content_types=['document'])
def doc_message(message):
    chat_id = message.chat.id
    if chat_id in users:
        ext = message.document.mime_type[-3:]
        users[chat_id]['img'] = None
        users[chat_id]['type'] = None
        if message is not None and message.document is not None and message.document.file_id is not None and (ext == 'png' or ext == 'jpg'):
            if DEBUG:
                logger(f"User: {chat_id}\tОтправил изображение")
            users[chat_id]['img'] = message.document.file_id
            users[chat_id]['type'] = 'document'
            bot.send_message(chat_id, 'Нажмите кнопку или отправьте новое изображение', reply_markup=gen_markup())
        else:
            if DEBUG:
                logger(f"User: {chat_id}\tОтправил изображение в не правильном формате")
            bot.send_message(chat_id, 'Не верный формат. Нужно отправить изображение в формате jpg и png')
    else:
        bot.send_message(chat_id, 'Сначала вы должны стартовать бот коммандой /start')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call is None and call.data is None:
        logger(f"Error in callback")
    elif call.data == "send_back":
        if users[call.from_user.id]['type'] == 'photo':
            bot.send_photo(call.from_user.id, users[call.from_user.id]['img'])
        elif users[call.from_user.id]['type'] == 'document':
            bot.send_document(call.from_user.id, users[call.from_user.id]['img'])
