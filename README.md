# Wildberries Sales Analytics Bot

This is a Telegram bot designed to help Wildberries sellers track sales, manage stores, and receive sales reports directly in Telegram. The bot allows users to add multiple stores, delete them, and get detailed sales reports for a selected store.

## Features

- **/start** - Start the bot and receive a welcome message.
- **/help** - Get a list of available commands.
- **/addshop** - Add a new store by providing the store name and API key.
- **/delshop** - Delete an existing store after confirmation.
- **/shops** - View the list of added stores.
- **/report** - Get a sales report for a selected store for a specific period:
  - "Today"
  - "Yesterday"
  - "Last 7 days"
  - Custom period (start and end dates)

## Requirements

- Python 3.8+
- Install dependencies using `pip`:
  - `aiogram` (version 3.x)
  - `json`
  - `aiohttp` (if needed for API requests)

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/wildberries-sales-bot.git
