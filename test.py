import requests
import json
import telebot

TELEGRAM_API_TOKEN = '5557598861:AAEWNX3OlKQKLxCU3rYie5ojNq6VAusVQmo'
ETH_PRICE_API_TOKEN = '6658c85d110e3bc23bd829f5eb4558899a1b51b64bb6649f881e44022c20'

etherPrice1 = requests.get('https://api.cryptorank.io/v1/currencies?api_key=6658c85d110e3bc23bd829f5eb4558899a1b51b64bb6649f881e44022c20')
etherPrice2 = json.loads(etherPrice1.text)
finalEtherPrice = etherPrice2["data"][1]["values"]["USD"]["price"]

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hi, i can:\n1. /eth_getBalance\n2. /eth_call')


@bot.message_handler(commands=['eth_getBalance'])
def get_balance(message):
    bot.send_message(message.chat.id, 'Please, type address:')

    @bot.message_handler(func=lambda answer: True)
    def echo_message(answer):
        response = requests.post("https://rpc.ankr.com/eth", json={"method": "eth_getBalance", "params": [answer.text, "latest"], "id": 1, "jsonrpc": "2.0"})
        address = json.loads(response.text)
        balance = address["result"]
        dec_balance = int(balance, base=16)
        real_balance = dec_balance * 10 ** -18 * finalEtherPrice
        bot.send_message(answer.chat.id, real_balance)


bot.infinity_polling()
