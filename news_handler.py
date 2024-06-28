import requests
import pandas as pd
from api_tokens import CRYPTOPANIC_TOKEN
from api_urls import CRYPTOPANIC_NEWS_URL


def handle_news_command(bot, message):
        url = CRYPTOPANIC_NEWS_URL

        args = message.text.split()[1:]
        if len(args) != 1:
            bot.reply_to(message, "Please provide cryptocurrency.")
            return

        coin = args
        params = {
            'auth_token': CRYPTOPANIC_TOKEN,
            'currencies': coin,
            'kind': 'news'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            
            df = pd.json_normalize(data['results'])
            max_likes = df.groupby('title')['votes.liked'].max()
            max_likes_filtered = max_likes[max_likes >= 1]
            max_liked_titles_df = df[df['votes.liked'].isin(max_likes_filtered)]

            result_df = max_liked_titles_df[['title', 'url']]

            message_text = ""
            for index, row in result_df.iterrows():
                message_text += f"{row['title']}: {row['url']}\n"

            bot.reply_to(message, message_text)
        else:
            bot.reply_to(message, f"Error: {response.status_code}")