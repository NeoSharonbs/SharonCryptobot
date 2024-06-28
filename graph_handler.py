
import requests
import pandas as pd
import matplotlib.pyplot as plt
from api_urls import COINGECKO_PRICE_GRAPH_URL


def handle_graph_command(bot, message):
        url = COINGECKO_PRICE_GRAPH_URL
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "Please provide both cryptocurrency, currency and days.")
            return

        coin, currency, days = args
        params = {
            'ids': coin,
            'vs_currencies': currency,
            'days':days
        }

        if days.isdigit() and int(days) <= 0:
           return bot.reply_to(message, "Number of days must be positive.")

        formatted_url = url.format(id=params['ids'], currency=params['vs_currencies'], days=params['days'])
        
        response = requests.get(formatted_url)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()

            df['price_change'] = df['price'].diff()

            plt.figure(figsize=(10, 6))
            plt.title(f'{coin.capitalize()} Price Over Last {days} Days In {currency.upper()}')
            plt.grid(True)

            for i in range(1, len(df)):
                color = 'green' if df.loc[i, 'price_change'] > 0 else 'red'
                plt.plot(df.loc[i-1:i, 'timestamp'], df.loc[i-1:i, 'price'], color=color, marker='o')
            plt.xticks(rotation=30, fontsize=10)

            plt.savefig('graph.jpg', format='jpg')

            bot.send_photo(message.chat.id, open('graph.jpg', 'rb'), caption=f"Here's the {coin.capitalize()} Price Over Last {days} Days In {currency.upper()}")

        else:
            bot.reply_to(message, f'Error: {response.status_code}')