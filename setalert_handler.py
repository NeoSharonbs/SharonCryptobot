import requests
from api_urls import COINGECKO_PRICE_URL

user_target_lst = []

def handle_setalert_command(bot, message):
        url = COINGECKO_PRICE_URL
        # Extracting arguments from the message
        # Splits the message into 2 words, and ignore the /setalert using [1:]
        args = message.text.split()[1:]
        if len(args) != 4:
            bot.reply_to(message, "Please provide cryptocurrency, currency, condition: above/below and target price.")
            return

        # Extracting coin and currency from the arguments
        coin, currency, condition, target_price_str = args

        try:
            target_price = float(target_price_str)
        except ValueError:
            bot.reply_to(message, "Target price must be a valid number.")
            return

        params = {
            'ids': coin,
            'vs_currencies': currency
        }

        user_target_params = {
            'ids': coin,
            'vs_currencies': currency,
            'condition': condition,
            'price_target': target_price,
            'chat_id': message.chat.id
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
                formatted_target_price = format_currency(target_price)
                currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}
                currency_symbol = currency_symbols.get(currency.lower(), currency.upper())

                if condition == 'above' and price > target_price:
                    bot.reply_to(message, f'{coin.capitalize()} price is already above {currency_symbol}{formatted_target_price}')
                elif condition == 'below' and price < target_price:
                    bot.reply_to(message, f'{coin.capitalize()} price is already below {currency_symbol}{formatted_target_price}')
                else:
                    bot.reply_to(message, f'{coin.capitalize()} target set: {currency_symbol}{formatted_target_price} {condition} {currency_symbol}{formatted_price}')
                    user_target_lst.append(user_target_params)
            else:
                bot.reply_to(message, f'Invalid coin or currency.')
        else:
            bot.reply_to(message, f'Error: {response.status_code}')