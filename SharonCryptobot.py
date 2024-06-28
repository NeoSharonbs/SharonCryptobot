import telebot
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import time
import threading
from api_tokens import TELEBOT_TOKEN, CRYPTOPANIC_TOKEN
from api_urls import COINGECKO_PRICE_URL, CRYPTOPANIC_NEWS_URL, COINGECKO_PRICE_GRAPH_URL


user_target_lst = []

# Function to create the bot
def create_bot(token):
    bot = telebot.TeleBot(token)


########## /cryptocurrency command ##########

    @bot.message_handler(commands=['cryptocurrency'])
    def Cryptocurrency(message):
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


########## /graph command ##########

    @bot.message_handler(commands=['graph'])
    def graph(message):
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
        

########## /news command ##########

    @bot.message_handler(commands=['news'])
    def news(message):
        url = CRYPTOPANIC_NEWS_URL

        args = message.text.split()[1:]
        if len(args) != 1:
            bot.reply_to(message, "Please provide cryptocurrency.")
            return

        # Extracting coin and currency from the arguments
        coin = args
        params = {
            'auth_token': CRYPTOPANIC_TOKEN,
            'currencies': coin,
            'kind': 'news'
        }

        # Make the GET request to the CryptoPanic API
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Load the data into a DataFrame
            df = pd.json_normalize(data['results'])

            # Group by title and get the maximum liked votes
            max_likes = df.groupby('title')['votes.liked'].max()

            # Filter out only titles with more than 1 like
            max_likes_filtered = max_likes[max_likes >= 1]

            # Filter the dataframe to include only titles with max liked votes
            max_liked_titles_df = df[df['votes.liked'].isin(max_likes_filtered)]

            # Extract title and url columns
            result_df = max_liked_titles_df[['title', 'url']]

            # Construct the message with titles and URLs
            message_text = ""
            for index, row in result_df.iterrows():
                message_text += f"{row['title']}: {row['url']}\n"

            # Reply to the user with the message
            bot.reply_to(message, message_text)
        else:
            bot.reply_to(message, f"Error: {response.status_code}")


########## /setalert command ##########

    @bot.message_handler(commands=['setalert'])
    def setalert(message):
        url = COINGECKO_PRICE_URL
        # Extracting arguments from the message
        # Splits the message into 2 words, and ignore the /setalert using [1:]
        args = message.text.split()[1:]
        if len(args) != 4:
            bot.reply_to(message, "Please provide cryptocurrency, currency, condition: above/below and target price.")
            return

        # Extracting coin and currency from the arguments
        coin, currency, condition, target_price = args

        target_price = int(target_price)

        params = {
            'ids': coin,
            'vs_currencies': currency
        }

        user_target_params = {
            'ids': coin,
            'vs_currencies': currency,
            'condition':condition,
            'price_target':target_price,
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

                if condition == 'above' and target_price > price:
                    bot.reply_to(message, f'{coin.capitalize()} target is set to: {currency_symbol}{formatted_target_price}\nCurrent {coin.capitalize()} price: {currency_symbol}{formatted_price}')
                    user_target_lst.append(user_target_params)
                elif condition == 'below' and target_price < price:
                    bot.reply_to(message, f'{coin.capitalize()}  target is set to: {currency_symbol}{formatted_target_price}\nCurrent {coin.capitalize()} price: {currency_symbol}{formatted_price}')
                    user_target_lst.append(user_target_params)
                else:
                    bot.reply_to(message, f'wrong target, cryptocurrency price is already:{price}')
            else:
                bot.reply_to(message, f'Invalid coin or currency.')
        else:
            bot.reply_to(message, f'Error: {response.status_code}')


########## /help command ##########

    @bot.message_handler(commands=['help'])
    def help(message):
        bot.reply_to(message, "Here are the available commands:\n"
                              "/cryptocurrency: Check cryptocurrency price.\n"
                              "Usage: /cryptocurrency [cryptocurrency] [currency]\n"
                              "Example: /cryptocurrency bitcoin usd\n"
                              "\n"
                              "/graph: Check cryptocurrency price over a specified number of days.\n"
                              "Usage: /graph [cryptocurrency] [currency] [days]\n"
                              "Example: /graph bitcoin usd 30\n"
                              "\n"
                              "/news: Get top-rated cryptocurrency news.\n"
                              "Usage: /news [cryptocurrency]\n"
                              "Example: /news bitcoin\n"
                              "\n"
                              "/setalert: Set a price alert for a cryptocurrency.\n"
                              "Usage: /setalert [cryptocurrency] [currency] [condition: above/below] [target price]\n"
                              "Example: /setalert bitcoin usd above 50000")


########## check_price_alerts ##########
    def check_price_alerts():
        global user_target_lst
        url = COINGECKO_PRICE_URL

        while True:
            for alert in user_target_lst:
                params = {
                    'ids': alert['ids'],
                    'vs_currencies': alert['vs_currencies']
                }

                response = requests.get(url, params=params)
                
                # Function to format the currency
                def format_currency(price):
                    return '{:,.2f}'.format(price)

                if response.status_code == 200:
                    data = response.json()
                    current_price = data[alert['ids']][alert['vs_currencies']]
                    formatted_price = format_currency(current_price)
                    formatted_target_price = format_currency(alert['price_target'])
                    currency_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}
                    currency_symbol = currency_symbols.get(alert['vs_currencies'].lower(), alert['vs_currencies'].upper())

                    if alert['ids'] in data and alert['vs_currencies'] in data[alert['ids']]:
                        if alert['condition'] == 'above' and current_price > alert['price_target']:
                            message = f"{alert['ids'].capitalize()} price is above {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\n Current price: {currency_symbol}{formatted_price}"
                            bot.send_message(alert['chat_id'], message)
                            user_target_lst.remove(alert)  # Remove alert after sending message
                        elif alert['condition'] == 'below' and current_price < alert['price_target']:
                            message = f"{alert['ids'].capitalize()} price is below {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\n Current price: {currency_symbol}{formatted_price}"
                            bot.send_message(alert['chat_id'], message)
                            user_target_lst.remove(alert)  # Remove alert after sending message

            time.sleep(30)  # Check alerts every 30 seconds

    # Start the thread for checking alerts
    alert_thread = threading.Thread(target=check_price_alerts)
    alert_thread.daemon = True
    alert_thread.start()

    return bot


if __name__ == '__main__':
    bot = create_bot(TELEBOT_TOKEN)
    bot.polling()