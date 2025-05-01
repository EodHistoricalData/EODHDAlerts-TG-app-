## Installing and Configuring Telegram ##

1. [Install Telegram](https://telegram.org/apps)

2. Open: [https://telegram.me/BotFather](https://telegram.me/BotFather)

3. Send the message /newbot to BotFather and follow the prompts

- Give your bot a name E.g. EODHDAlerts

- Assign a username (must end in _bot) E.g. eodhdalerts_bot

        Done! Congratulations on your new bot. You will find it at t.me/eodhdalerts_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

        Use this token to access the HTTP API:
        <YOUR_TOKEN>
        Keep your token secure and store it safely, it can be used by anyone to control your bot.

        For a description of the Bot API, see this page: https://core.telegram.org/bots/api

 - Add <YOUR_TOKEN> to TELEGRAM_BOT_TOKEN in config.py

4. Retrieve your Client ID (not a simple task!)

- Open your new bot E.g. [https://t.me/eodhdalerts_bot](https://t.me/eodhdalerts_bot)

- **IMPORTANT** - Send at least one message to your newly created bot E.g. "hello"

- Browse to [https://api.telegram.org/botYOUR_TOKEN/getUpdates](https://api.telegram.org/botYOUR_TOKEN/getUpdates) <- Replace “YOUR_TOKEN” with the token

- Add the "id" to TELEGRAM_CHAT_ID in config.py
    

## Bot Commands ##

    /start: Welcome message.

    /set_symbol BTC-USD: Change the trading symbol.

    /set_interval 1h: Change the data interval.

    /get_price: Retrieve the current price.