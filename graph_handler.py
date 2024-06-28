
import requests
import pandas as pd
import matplotlib.pyplot as plt
from api_urls import COINGECKO_PRICE_GRAPH_URL


def handle_graph_command(bot, message):
        url = COINGECKO_PRICE_GRAPH_URL
        # Extracting arguments from the message
        # Splits the message into 2 words, and ignore the /graph using [1:]
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "Please provide both cryptocurrency, currency and days.")
            return

        # Extracting coin and currency from the arguments
        coin, currency, days = args
        params = {
            'ids': coin,
            'vs_currencies': currency,
            'days':days
        }

        # Validate days
        if days.isdigit() and int(days) <= 0:
           return bot.reply_to(message, "Number of days must be positive.")

        # Format URL
        formatted_url = url.format(id=params['ids'], currency=params['vs_currencies'], days=params['days'])
        
        # Sending request to CoinGecko API
        response = requests.get(formatted_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()

            # Calculate price changes
            df['price_change'] = df['price'].diff()

            # Plotting the data
            plt.figure(figsize=(10, 6))
            plt.title(f'{coin.capitalize()} Price Over Last {days} Days In {currency.upper()}')
            plt.grid(True)

            # Plot with conditional colors
            for i in range(1, len(df)):
                color = 'green' if df.loc[i, 'price_change'] > 0 else 'red'
                plt.plot(df.loc[i-1:i, 'timestamp'], df.loc[i-1:i, 'price'], color=color, marker='o')
            plt.xticks(rotation=30, fontsize=10)

            # Save the plot as a JPG file
            plt.savefig('graph.jpg', format='jpg')

            bot.send_photo(message.chat.id, open('graph.jpg', 'rb'), caption=f"Here's the {coin.capitalize()} Price Over Last {days} Days In {currency.upper()}")

        else:
            bot.reply_to(message, f'Error: {response.status_code}')