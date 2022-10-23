import requests
import json
import telebot
from config import TELEGRAM_API_TOKEN, ETH_PRICE_API_TOKEN
from web3 import Web3, HTTPProvider

f = open('config.json')
token_info_map = json.load(f)
ether_price = json.loads(requests.get('https://api.cryptorank.io/v1/currencies?api_key' + ETH_PRICE_API_TOKEN).text)
final_ether_price = ether_price["data"][1]["values"]["USD"]["price"]

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hi, i can:\n1. /eth_getBalance\n2. /eth_call')


@bot.message_handler(commands=['eth_getBalance'])
def get_balance(message):
    bot.send_message(message.chat.id, 'Please, type address:')

    @bot.message_handler(func=lambda answer: True)
    def echo_message(answer):
        response = requests.post("https://rpc.ankr.com/eth",
                                 json={"method": "eth_getBalance",
                                       "params": [answer.text, "latest"],
                                       "id": 1, "jsonrpc": "2.0"})
        address = json.loads(response.text)
        balance = address["result"]
        dec_balance = int(balance, base=16)
        real_balance = dec_balance * 10 ** -18 * final_ether_price
        bot.send_message(answer.chat.id, str(dec_balance * 10 ** -18) + " ETH")
        bot.send_message(answer.chat.id, str(real_balance) + " USD")


@bot.message_handler(commands=['eth_call'])
def eth_call(message):
    msg = bot.send_message(message.chat.id, 'Choose token:\n1. /Tether_USD(USDT)\n2. /USD_Coin(USDC)\n'
                                            '3. /BNB(BNB)\n4. /Binance_USD(BUSD)\n5. /Matic_Token(MATIC)\n'
                                            '6. /Dai_Stablecoin(DAI)\n7. /SHIBA_INU(SHIB)\n8. /stETH(stETH)\n'
                                            '9. /HEX(HEX)\n10. /Theta_Token(THETA)')
    bot.register_next_step_handler(msg, second_step)


def second_step(message):
    bot.send_message(message.chat.id, 'Please, type address:')
    bot.register_next_step_handler(message, third_step, token_info_map[message.text.replace("/", "")])


def third_step(message, *args):
    token_name = args[0]["Name"]
    token_address = args[0]["Address"]
    coefficient = args[0]["Decimals"]
    final_token_price = 0
    for i in range(len(ether_price["data"])):
        if ether_price["data"][i]["name"] == token_name:
            final_token_price = ether_price["data"][i]["values"]["USD"]["price"]
    w3 = Web3(HTTPProvider('https://rpc.ankr.com/eth'))
    abi = '[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],' \
          '"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],' \
          '"payable":false,"stateMutability":"view","type":"function"}] '
    my_contract = w3.eth.contract(address=token_address, abi=abi)
    response = my_contract.functions.balanceOf(message.text).call()
    dec_token_balance = int(response)
    real_token_balance = dec_token_balance / 10 ** coefficient
    print(final_token_price)
    print(int(real_token_balance))
    print(str(int(real_token_balance) * final_token_price))
    bot.send_message(message.chat.id, str(real_token_balance) + " " + token_name)
    bot.send_message(message.chat.id, str(int(real_token_balance) * final_token_price) + " USD")


bot.infinity_polling()
