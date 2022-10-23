import requests
import json
import telebot
from config import TELEGRAM_API_TOKEN, ETH_PRICE_API_TOKEN
from web3 import Web3, HTTPProvider


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
        bot.send_message(answer.chat.id, real_balance)


def show_token_balance(answer, token_address, token_name, coefficient):
    bot.send_message(answer.chat.id, 'Please, type address:')

    @bot.message_handler(func=lambda answ: True)
    def echo_message(answ):
        final_token_price = 0
        for i in range(len(ether_price["data"])):
            if ether_price["data"][i]["name"] == token_name:
                final_token_price = ether_price["data"][i]["values"]["USD"]["price"]
        w3 = Web3(HTTPProvider('https://rpc.ankr.com/eth'))
        abi = '[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],' \
              '"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],' \
              '"payable":false,"stateMutability":"view","type":"function"}] '
        my_contract = w3.eth.contract(address=token_address, abi=abi)
        response = my_contract.functions.balanceOf(answ.text).call()
        dec_token_balance = int(response)
        real_token_balance = dec_token_balance * 10 ** coefficient
        bot.send_message(answ.chat.id, str(real_token_balance) + " " + token_name)
        bot.send_message(answ.chat.id, str(int(real_token_balance) * final_token_price) + " USD")


@bot.message_handler(commands=['eth_call'])
def eth_call(message):
    bot.send_message(message.chat.id, 'Choose token:\n1. /Tether_USD(USDT)\n2. /USD_Coin(USDC)\n'
                                      '3. /BNB(BNB)\n4. /Binance_USD(BUSD)\n5. /Matic_Token(MATIC)\n'
                                      '6. /Dai_Stablecoin(DAI)\n7. /SHIBA_INU(SHIB)\n8. /stETH(stETH)\n'
                                      '9. /HEX(HEX)\n10. /Theta_Token(THETA)')

    @bot.message_handler(commands=['Tether_USD'])
    def tether(answer):
        show_token_balance(answer, "0xdAC17F958D2ee523a2206206994597C13D831ec7", "Tether", -6)

    @bot.message_handler(commands=['USD_Coin'])
    def usd_coin(answer):
        show_token_balance(answer, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USD Coin", -6)

    @bot.message_handler(commands=['BNB'])
    def bnb(answer):
        show_token_balance(answer, "0xB8c77482e45F1F44dE1745F52C74426C631bDD52", "BNB", -18)

    @bot.message_handler(commands=['Binance_USD'])
    def binance_usd(answer):
        show_token_balance(answer, "0x4Fabb145d64652a948d72533023f6E7A623C7C53", "Binance USD", -18)

    @bot.message_handler(commands=['Matic_Token'])
    def matic_token(answer):
        show_token_balance(answer, "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0", "Polygon", -18)

    @bot.message_handler(commands=['Dai_Stablecoin'])
    def dai_stablecoin(answer):
        show_token_balance(answer, "0x6B175474E89094C44Da98b954EedeAC495271d0F", "Dai", -18)

    @bot.message_handler(commands=['SHIBA_INU'])
    def shiba_inu(answer):
        show_token_balance(answer, "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", "SHIBA INU", -18)

    # @bot.message_handler(commands=['stETH'])
    # def steth(answer):
    #     show_token_balance(answer, "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", "stETH", -18)
    #
    # @bot.message_handler(commands=['HEX'])
    # def hex_coin(answer):
    #     show_token_balance(answer, "0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39", "HEX", -18)

    @bot.message_handler(commands=['Theta_Token'])
    def theta_token(answer):
        show_token_balance(answer, "0x3883f5e181fccaF8410FA61e12b59BAd963fb645", "Theta Token", -18)


bot.infinity_polling()
