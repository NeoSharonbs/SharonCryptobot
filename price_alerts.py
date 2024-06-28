import requests
import time
from api_urls import COINGECKO_PRICE_URL

user_target_lst = []  # List to store user-set price alerts

# Function to check price alerts
def check_price_alerts(bot):
    global user_target_lst
    url = COINGECKO_PRICE_URL

    while True:
        for alert in user_target_lst:
            params = {
                'ids': alert['ids'],
                'vs_currencies': alert['vs_currencies']
            }

            response = requests.get(url, params=params)

            def format_currency(price):
                return '{:,.2f}'.format(price)

            if response.status_code == 200:
                data = response.json()
                if alert['ids'] in data and alert['vs_currencies'] in data[alert['ids']]:
                    current_price = data[alert['ids']][alert['vs_currencies']]
                    formatted_price = format_currency(current_price)
                    formatted_target_price = format_currency(alert['price_target'])
                    currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}
                    currency_symbol = currency_symbols.get(alert['vs_currencies'].lower(), alert['vs_currencies'].upper())

                    if alert['condition'] == 'above' and current_price > alert['price_target']:
                        message = f"{alert['ids'].capitalize()} price is above {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\n Current price: {currency_symbol}{formatted_price}"
                        bot.send_message(alert['chat_id'], message)
                        user_target_lst.remove(alert)  # Remove alert after sending message
                    elif alert['condition'] == 'below' and current_price < alert['price_target']:
                        message = f"{alert['ids'].capitalize()} price is below {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\n Current price: {currency_symbol}{formatted_price}"
                        bot.send_message(alert['chat_id'], message)
                        user_target_lst.remove(alert)  # Remove alert after sending message

        time.sleep(30)  # Check alerts every 30 seconds
