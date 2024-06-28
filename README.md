# Cryptocurrency Telegram Bot

## Description
This Python script implements a Telegram bot that provides various functionalities related to cryptocurrencies using the CoinGecko and CryptoPanic APIs. It allows users to check cryptocurrency prices, generate price graphs, fetch top-rated cryptocurrency news, and set price alerts.

## Features
- **/cryptocurrency**: Check current cryptocurrency prices.
- **/graph**: Generate a price graph over a specified number of days.
- **/news**: Fetch top-rated news related to a cryptocurrency.
- **/setalert**: Set price alerts for cryptocurrencies.
- **/help**: Provides a list of available commands and their usage examples.

## Setup
1. Install Python (if not already installed).
2. Install required libraries using `pip install -r requirements.txt`.
3. Obtain API tokens for Telegram (`TELEBOT_TOKEN`) and CryptoPanic (`CRYPTOPANIC_TOKEN`).
4. Create `api_tokens.py` and `api_urls.py` files with your tokens and URLs respectively (not included in this repository).
5. Run the script using `python bot.py`.

## Dependencies
- telebot
- requests
- pandas
- matplotlib

## Usage
1. Start the bot by running `python bot.py`.
2. Interact with the bot via Telegram using the provided commands.