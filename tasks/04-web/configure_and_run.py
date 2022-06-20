import yaml
from waitress import serve

from server import bot, app
from server import logger, run_ngrok
from server import TOKEN, HOST, PORT

if __name__ == '__main__':
    logger("Starting web-application")
    bot.remove_webhook()
    ngrok_url = run_ngrok()
    logger("Ngrok service started")
    bot.set_webhook(url=f'{ngrok_url}/{TOKEN}')
    logger("Webhook set")
    logger("Web-application ready!")
    serve(app, host=HOST, port=PORT)
