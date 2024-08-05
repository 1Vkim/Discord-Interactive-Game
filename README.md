
# Discord Bot

## Introduction
This is a Discord bot built using `discord.py` that offers various features including banking, working, buying/selling items, robbing other users, and interacting with pets.

## Prerequisites
- Python 3.7 or higher
- `discord.py` library
- `requests` library
- `sqlite3` library
- `random` library
- `replit` for database management

## Setup

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies:**
   ```sh
   pip install discord.py requests sqlite3 random replit
   ```

3. **Create a `.env` file in the root directory and add your Discord bot token:**
   ```env
   DISCORD_TOKEN=<your-discord-bot-token>
   ```

4. **Run the bot:**
   ```sh
   python bot.py
   ```

## Commands

### General Commands

- **`/hello`**
  - Responds with a greeting message.

- **`/balance [user]`**
  - Displays the balance of the user.

### Banking Commands

- **`/bank`**
  - Moves all money from the purse to the bank.

- **`/withdraw [amount]`**
  - Withdraws a specified amount from the bank to the purse.

### Work Commands

- **`/work`**
  - Sends a trivia question to the user. Correct answers earn $100, incorrect answers earn $1.

### News Commands

- **`/news`**
  - Sends the latest news articles to the user. Costs $10.

### Item Commands

- **`/buy [item] [quantity]`**
  - Buys a specified quantity of an item.

- **`/sell [target] [item] [price]`**
  - Proposes selling an item to another user at a specified price.

- **`/accept [seller_id] [item] [price]`**
  - Accepts a trade proposal to buy an item from another user.

- **`/swap [target] [your_item] [their_item]`**
  - Proposes swapping an item with another user.

- **`/acceptswap [proposer_id] [your_item] [their_item]`**
  - Accepts a swap proposal from another user.

### Robbery Commands

- **`/rob [target]`**
  - Attempts to rob another user. The success chance can be increased by paying $100.

- **`/bankrob`**
  - Attempts a high-stakes robbery of the bank. The success chance can be increased by paying $100.

### Pet Commands

- **`/buy_pet [pet_type]`**
  - Buys a pet of a specified type.

- **`/pet_status`**
  - Displays the status of the user's pets.

- **`/pay_pet_cost [pet_type]`**
  - Pays the recurring cost for a specified pet.

### Ranking Command

- **`/rank`**
  - Displays the rankings of users based on their total value (bank balance, purse balance, and items).

## License
This project is licensed under the MIT License.
```
