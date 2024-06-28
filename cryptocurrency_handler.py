import requests
from api_urls import COINGECKO_PRICE_URL


########## /cryptocurrency command ##########

def handle_cryptocurrency_command(bot, message):
        url = COINGECKO_PRICE_URL
        # Extracting arguments from the message
        # Splits the message into 2 words, and ignore the /Cryptocurrency using [1:]
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "Please provide both cryptocurrency and currency.")
            return

        # Extracting coin and currency from the arguments
        coin, currency = args
        params = {
            'ids': coin,
            'vs_currencies': currency
        }

        # Function to format the currency
        def format_currency(price):
            return '{:,.2f}'.format(price)

        # Sending request to CoinGecko API
        response = requests.get(url, params=params)

        # Handling the response
        if response.status_code == 200:
            data = response.json()
            if coin in data and currency in data[coin]:
                price = data[coin][currency]
                formatted_price = format_currency(price)
                currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}
                currency_symbol = currency_symbols.get(currency.lower(), currency.upper())
                bot.reply_to(message, f'{coin.capitalize()} price in {currency.upper()}: {currency_symbol}{formatted_price}')
            else:
                bot.reply_to(message, f'Invalid coin or currency.')
        else:
            bot.reply_to(message, f'Error: {response.status_code}')