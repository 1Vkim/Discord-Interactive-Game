import asyncio
from datetime import datetime
import discord
import os,requests,json,random
from replit import db
import sqlite3
from discord.ext import commands

import sportscrape 



intents = discord. Intents.default()
intents. message_content = True
intents .members = True
bot = commands.Bot(intents=intents, command_prefix='/')

def instanciateItems(): 
  if 'pets' in db.keys():
    del db['pets']
  db['pets'] = {
      "Dog": {"icon": "dog.png", "cost": 500, "stock": 10, "maintenance_cost": 50, "hunger_rate": 2, "happiness_rate": 3},
      "Cat": {"icon": "cat.png", "cost": 400, "stock": 15, "maintenance_cost": 40, "hunger_rate": 3, "happiness_rate": 2},
      "Rabbit": {"icon": "rabbit.png", "cost": 300, "stock": 20, "maintenance_cost": 30, "hunger_rate": 4, "happiness_rate": 1},
      "Hamster": {"icon": "hamster.png", "cost": 200, "stock": 25, "maintenance_cost": 20, "hunger_rate": 5, "happiness_rate": 2},
      "Fish": {"icon": "fish.png", "cost": 100, "stock": 30, "maintenance_cost": 10, "hunger_rate": 1, "happiness_rate": 1},
      "Parrot": {"icon": "parrot.png", "cost": 600, "stock": 8, "maintenance_cost": 60, "hunger_rate": 3, "happiness_rate": 4},
      "Turtle": {"icon": "turtle.png", "cost": 350, "stock": 12, "maintenance_cost": 25, "hunger_rate": 2, "happiness_rate": 2},
      "Snake": {"icon": "snake.png", "cost": 450, "stock": 10, "maintenance_cost": 40, "hunger_rate": 1, "happiness_rate": 3},
      "Lizard": {"icon": "lizard.png", "cost": 300, "stock": 15, "maintenance_cost": 30, "hunger_rate": 2, "happiness_rate": 2},
      "Spider": {"icon": "spider.png", "cost": 150, "stock": 20, "maintenance_cost": 15, "hunger_rate": 4, "happiness_rate": 1}
  }



def ensure_user_initialized(user_id):
    if user_id not in db or db[user_id] is None:
        db[user_id] = {'purse': 0, 'bank': 0, 'items': {}, 'pets': {}}
        db
    if 'items' not in db[user_id]:
        db[user_id]['items'] = {}


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    #instanciateItems()
    # Initialize database with default structure if it doesn't exist
    if "items" not in db:
        db["items"] = {}
        db["users"]= {"Police":{"bank":1000,"purse": 0, "items": {}}}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    ensure_user_initialized(user_id)

    if message.content == '$hello':
        await message.channel.send(f"Hello there <@{message.author.id}>! How may I assist you?")
    else:
        await bot.process_commands(message)


def check_user(id):
    return id in db

@bot.command()
async def bank(ctx):
    user_id = str(ctx.author.id)
    if check_user(user_id):
        db[user_id]['bank'] += db[user_id]['purse']
        db[user_id]['purse'] = 0

    await ctx.send(await balance_str(ctx))

@bot.command()
async def withdraw(ctx, amount: float = 0):
    user_id = str(ctx.author.id)
    if check_user(user_id):
        if db[user_id]['bank'] < amount:
            await ctx.send('You do not have enough money to withdraw')
            return
        db[user_id]['bank'] -= amount
        db[user_id]['purse'] += amount

    await ctx.send(await balance_str(ctx))

@bot.command()
async def work(ctx):
    if ctx.guild:  # Only delete the message if it's in a guild channel
        await ctx.message.delete()

    # Get some trivia questions for the work
    result = requests.get("https://the-trivia-api.com/api/questions/")
    questions = result.json()[:4]  # Select the first four elements
    question = questions[0]['question']
    correctAnswer = questions[0]['correctAnswer']
    incorrectAnswers = questions[0]['incorrectAnswers']

    answers = incorrectAnswers + [correctAnswer]
    random.shuffle(answers)

    view = discord.ui.View()


    async def button_callback(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        ensure_user_initialized(user_id)

        if interaction.data['custom_id'] == correctAnswer:
            await interaction.response.send_message("Correct, you have earned $100")
            db[user_id]['bank'] += 100
        else:
            await interaction.response.send_message("Wrong, you have earned $1 for trying")
            db[user_id]['bank'] += 1

        await interaction.message.delete()

    for answer in answers:
        button = discord.ui.Button(label=answer, style=discord.ButtonStyle.green, custom_id=answer)
        button.callback = button_callback
        view.add_item(button)

    await ctx.author.send(content=question, view=view)


@bot.command()
async def news(ctx):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)

    newspaper_price = 10
    if db[user_id]['purse'] >= newspaper_price:
        db[user_id]['purse'] -= newspaper_price
    elif db[user_id]['bank'] >= newspaper_price:
        db[user_id]['bank'] -= newspaper_price
    else:
        await ctx.send("You do not have enough money to buy the newspaper.")
        return

    conn = sqlite3.connect('scraped_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM articles')
    articles = cursor.fetchall()
    conn.close()

    news_message = "Here are the latest news articles:\n"
    for article in articles:
        news_message += f"- {article[0]}\n"

    await ctx.author.send(news_message)

@bot.command()
async def buy(ctx, item: str = None, quantity: int = 1):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)

    if item is None:
        await ctx.send("Here are the items available to buy")
        for_sale = "```"
        for name, item_data in db['items'].items():
            if item_data['stock'] > 0:
                for_sale += (f"{name}\t${item_data['cost']}\t[{item_data['stock']} remaining]\n")
        for_sale += "```"
        await ctx.send(for_sale)
    else:
        if item in db['items']:
            item_data = db['items'][item]
            if item_data['stock'] < quantity:
                await ctx.send(f"Not enough stock for {item}. Only {item_data['stock']} remaining.")
                return

            total_cost = item_data['cost'] * quantity
            if db[user_id]['bank'] < total_cost:
                await ctx.send(f'You do not have enough money to buy {quantity} {item}(s). Total cost: ${total_cost}')
                return

            db[user_id]['bank'] -= total_cost
            db['items'][item]['stock'] -= quantity
            if item not in db[user_id]['items']:
                db[user_id]['items'][item] = 0
            db[user_id]['items'][item] += 1
            await ctx.send(f"Purchase successful. You bought {item}.")
        else:
            await ctx.send('Item not available or out of stock.')



@bot.command()
async def rob(ctx, target: discord.Member = True):
    robber_id = str(ctx.author.id)
    target_id = str(target.id)
    ensure_user_initialized(robber_id)
    ensure_user_initialized(target_id)

    if db[target_id]['purse'] == 0:
        await ctx.send(f"{target.mention} has nothing to rob.")
        return


    base_success_chance = 20  # Base success chance is 20%
    await ctx.send(f"{ctx.author.mention}, do you want to increase your chances of a successful robbery by paying $100? Current success chance: {base_success_chance}%", view=create_robbery_view(ctx, robber_id, target_id, base_success_chance, target.mention))


def create_robbery_view(ctx,  robber_id, target_id, success_chance, target_mention):
    view = discord.ui.View()

    increase_chance_button = discord.ui.Button(label="Increase Chances", style=discord.ButtonStyle.primary)
    proceed_button = discord.ui.Button(label="Proceed with Robbery", style=discord.ButtonStyle.danger)

    async def increase_chance_callback(interaction: discord.Interaction):
        if interaction.user.id != int(robber_id):
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

        if db[robber_id]['purse'] < 100:
            await interaction.response.send_message("You don't have enough money to increase your chances!", ephemeral=True)
            return

        db[robber_id]['purse'] -= 100
        new_success_chance = success_chance + 20
        await interaction.response.edit_message(content=f"Your success chance has increased to {new_success_chance}%. Do you want to proceed with the robbery?", view=create_robbery_view(ctx, robber_id, target_id, new_success_chance))

    async def proceed_callback(interaction: discord.Interaction):
        if interaction.user.id != int(robber_id):
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

        dice_roll = random.randint(1, 100)
        if dice_roll <= success_chance:
            rob_amount = db[target_id]['purse']
            db[target_id]['purse'] = 0
            db[robber_id]['purse'] += rob_amount
            await interaction.response.send_message(f"Robbery successful! You robbed ${rob_amount} from {target_mention}.")
        else:
            db[robber_id]['purse'] = max(0, db[robber_id]['purse'] - 500)
            await interaction.response.send_message(f"Robbery failed! You were caught and fined $500.")

    increase_chance_button.callback = increase_chance_callback
    proceed_button.callback = proceed_callback

    view.add_item(increase_chance_button)
    view.add_item(proceed_button)

    return view

def create_initial_view(ctx, robber_id, target_id, rob_amount, target_mention):
    view = discord.ui.View()

    fight_back_button = discord.ui.Button(label="Fight Back", style=discord.ButtonStyle.danger)
    give_up_button = discord.ui.Button(label="Give Up", style=discord.ButtonStyle.secondary)

    async def fight_back_callback(interaction: discord.Interaction):
        if interaction.user.id != int(target_id):
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

        await interaction.response.send_message("You chose to fight back!", ephemeral=True)
        await ctx.send(f"{ctx.author.mention}, {target_mention} chose to fight back! What will you do?", view=create_robbery_view(ctx, robber_id, target_id))

    async def give_up_callback(interaction: discord.Interaction):
        if interaction.user.id != int(target_id):
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

        db[target_id]['purse'] -= rob_amount
        db[robber_id]['purse'] += rob_amount
        await ctx.send(f"{ctx.author.mention} successfully robbed ${rob_amount} from {target_mention}!")

    fight_back_button.callback = fight_back_callback
    give_up_button.callback = give_up_callback

    view.add_item(fight_back_button)
    view.add_item(give_up_button)

    return view

@bot.command()
async def rank(ctx):
    def calculate_user_value(user_id):
        user_data = db[user_id]
        total_value = user_data['bank'] + user_data['purse']

        for item_name, quantity in user_data['items'].items():
            item_value = db['items'][item_name]['cost']
            total_value += item_value * quantity

        return total_value

    # Gather all users
    users = []
    for key in db.keys():
        if key.isdigit():  # Assuming user IDs are stored as numeric keys
            users.append(key)

    # Calculate the total value for each user
    user_values = []
    for user_id in users:
        user_value = calculate_user_value(user_id)
        user_values.append((user_id, user_value))

    # Sort users by total value in descending order
    user_values.sort(key=lambda x: x[1], reverse=True)

    # Prepare the ranking message
    ranking_message = "User Rankings:\n"
    for i, (user_id, value) in enumerate(user_values, 1):
        user = await bot.fetch_user(int(user_id))
        ranking_message += f"{i}. {user.name}#{user.discriminator} - Total Value: ${value}\n"

    await ctx.send(ranking_message)
    
def calculate_total_loss():
    total_loss = 0
    for user in db['users'].values():
        total_loss += user['bank'] * 0.15
    return total_loss

def rob_success(user_id):
    total_loss = calculate_total_loss()
    for user in db['users'].values():
        user['bank'] -= user['bank'] * 0.15
    db['users'][user_id]['bank'] += total_loss

def distribute_fine_among_users(fine):
    total_users = len(db['users']) - 1  # Excluding the Police
    if total_users == 0:
        return  # No users to distribute to
    share = fine * 0.75 / total_users
    for user_id, user_data in db['users'].items():
        if user_id != 'Police':
            user_data['bank'] += share


@bot.command()
async def bankrob(ctx):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)


    async def step_one(interaction):
        if random.randint(1, 100) <= 20:
            await interaction.response.send_message("Step 1: Success! Proceeding to step 2...", ephemeral=True)
            await step_two(interaction)
        else:
            fine = 500
            db['users'][user_id]['bank'] -= fine
            db['users']['Police']['bank'] += fine
            distribute_fine_among_users(fine)
            await interaction.response.send_message("Step 1: Failed! You were arrested and fined $500.", ephemeral=True)

    async def step_two(interaction):
        if random.randint(1, 100) <= 50:
            await interaction.response.send_message("Step 2: Success! Proceeding to step 3...", ephemeral=True)
            await step_three(interaction)
        else:
            fine = 1000
            db['users'][user_id]['bank'] -= fine
            db['users']['Police']['bank'] += fine
            distribute_fine_among_users(fine)
            await interaction.response.send_message("Step 2: Failed! You were arrested and fined $1000.", ephemeral=True)

    async def step_three(interaction):
        if random.randint(1, 100) <= 75:
            rob_success()
            await interaction.response.send_message("Step 3: Success! You robbed 15% from every user's bank account!", ephemeral=True)
        else:
            fine = 1500
            db['users'][user_id]['bank'] -= fine
            db['users']['Police']['bank'] += fine
            distribute_fine_among_users(fine)
            await interaction.response.send_message("Step 3: Failed! You were arrested and fined $500.", ephemeral=True)

    # Check if the user has enough money to pay for a higher probability
    await ctx.send("Do you want to pay $100 to increase your probability of success? (yes/no)")

    def check(m):
        return m.author == ctx.author and m.content.lower() in ['yes', 'no']

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond.")
        return

    if msg.content.lower() == 'yes':
        if db['users'][user_id]['bank'] >= 100:
            db['users'][user_id]['bank'] -= 100
            await ctx.send("You paid $100. Your probability of success is increased!")
        else:
            await ctx.send("You don't have enough money to pay $100.")
            return

    view = discord.ui.View()
    button = discord.ui.Button(label="Attempt Robbery", style=discord.ButtonStyle.danger)

    async def button_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await step_one(interaction)
        else:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)

    button.callback = button_callback
    view.add_item(button)

    await ctx.send(f"{ctx.author.mention} is attempting a high-stakes robbery!", view=view)


@bot.command()
async def sell(ctx, target: discord.Member, item: str, price: int):
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    ensure_user_initialized(user_id)
    ensure_user_initialized(target_id)

    if item not in db['users'][user_id]['items']:
        await ctx.send("You don't own this item.")
        return

    await ctx.send(f"{target.mention}, {ctx.author.mention} wants to sell {item} to you for ${price}. Type `!accept {ctx.author.id} {item} {price}` to accept the trade.")

@bot.command()
async def accept(ctx, seller_id: int, item: str, price: int):
    user_id = str(ctx.author.id)
    seller_id = str(seller_id)
    ensure_user_initialized(user_id)
    ensure_user_initialized(seller_id)

    if db['users'][user_id]['bank'] < price:
        await ctx.send("You don't have enough money to buy this item.")
        return

    if item not in db['users'][seller_id]['items']:
        await ctx.send("The seller no longer has this item.")
        return

    db['users'][user_id]['bank'] -= price
    db['users'][seller_id]['bank'] += price
    db['users'][seller_id]['items'].remove(item)
    if item not in db['users'][user_id]['items']:
        db['users'][user_id]['items'][item] = 0
    db['users'][user_id]['items'][item] += 1

    await ctx.send(f"{ctx.author.mention} bought {item} from {bot.get_user(int(seller_id)).mention} for ${price}.")

@bot.command()
async def swap(ctx, target: discord.Member, your_item: str, their_item: str):
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    ensure_user_initialized(user_id)
    ensure_user_initialized(target_id)

    if your_item not in db['users'][user_id]['items']:
        await ctx.send("You don't own this item.")
        return

    if their_item not in db['users'][target_id]['items']:
        await ctx.send(f"{target.mention} doesn't own this item.")
        return

    await ctx.send(f"{target.mention}, {ctx.author.mention} wants to swap {your_item} for your {their_item}. Type `!acceptswap {ctx.author.id} {your_item} {their_item}` to accept the trade.")

@bot.command()
async def acceptswap(ctx, proposer_id: int, your_item: str, their_item: str):
    user_id = str(ctx.author.id)
    proposer_id = str(proposer_id)
    ensure_user_initialized(user_id)
    ensure_user_initialized(proposer_id)

    if their_item not in db['users'][proposer_id]['items']:
        await ctx.send(f"The proposer no longer has {their_item}.")
        return

    if your_item not in db['users'][user_id]['items']:
        await ctx.send(f"You no longer have {your_item}.")
        return

    db['users'][proposer_id]['items'].remove(their_item)
    db['users'][user_id]['items'].remove(your_item)

    if their_item not in db['users'][user_id]['items']:
        db['users'][user_id]['items'][their_item] = 0
    if your_item not in db['users'][proposer_id]['items']:
        db['users'][proposer_id]['items'][your_item] = 0

    db['users'][user_id]['items'][their_item] += 1
    db['users'][proposer_id]['items'][your_item] += 1

    await ctx.send(f"{ctx.author.mention} swapped their {your_item} with {bot.get_user(int(proposer_id)).mention}'s {their_item}.")

@bot.command()
async def buy_pet(ctx, pet_type: str = None):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)

    if pet_type is None:
        await ctx.send("Here are the pets available to buy")
        for_sale = "```"
        for name, item_data in db['pets'].items():
            if item_data['stock'] > 0:
                for_sale += f"{name}\t${item_data['cost']}\t[{item_data['stock']} remaining]\n"
        for_sale += "```"
        await ctx.send(for_sale)
    else:
        # Check if the pet type exists
        if pet_type not in db['pets']:
            await ctx.send("Invalid pet type.")
            return

        # Check if the user already owns a pet of the same type
        if pet_type in db['users'][user_id]['pets']:
            await ctx.send("You already own a pet of this type.")
            return

        # Deduct the cost of the pet from the user's bank balance
        pet_cost = db['pets'][pet_type]['cost']
        if db['users'][user_id]['bank'] < pet_cost:
            await ctx.send("You don't have enough money to buy this pet.")
            return

        db['users'][user_id]['bank'] -= pet_cost

        # Add the pet to the user's inventory
        db['users'][user_id]['pets'][pet_type] = {
            'health': 100,  # Initial health
            'last_payment_date': None  # Set to None as the pet hasn't started requiring recurring payments yet
        }

        await ctx.send(f"You bought a {pet_type}!")

@bot.command()
async def pet_status(ctx):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)

    if not db['users'][user_id]['pets']:
        await ctx.send("You don't own any pets.")
        return

    status_msg = "Your Pets:\n"
    for pet_type, pet_data in db['users'][user_id]['pets'].items():
        status_msg += f"{pet_type}: Health - {pet_data['health']}, Last Payment Date - {pet_data['last_payment_date']}\n"

    await ctx.send(status_msg)

@bot.command()
async def pay_pet_cost(ctx, pet_type: str):
    user_id = str(ctx.author.id)
    ensure_user_initialized(user_id)

    # Check if the user owns a pet of the specified type
    if pet_type not in db['users'][user_id]['pets']:
        await ctx.send("You don't own a pet of this type.")
        return

    # Check if it's time to pay the recurring cost
    if db['users'][user_id]['pets'][pet_type]['last_payment_date'] is None:
        await ctx.send("You don't need to pay for this pet yet.")
        return

    # Check if the user has enough money to pay the recurring cost
    pet_cost = db['pets'][pet_type]['recurring_cost']
    if db['users'][user_id]['bank'] < pet_cost:
        await ctx.send("You don't have enough money to pay for this pet.")
        return

    # Deduct the recurring cost from the user's bank balance
    db['users'][user_id]['bank'] -= pet_cost

    # Update the last payment date
    db['users'][user_id]['pets'][pet_type]['last_payment_date'] = datetime.now().date()

    await ctx.send("Recurring cost paid. Your pet is healthy!")


@bot.command()
async def balance(ctx, user: discord.Member = None):
    await ctx.send(await balance_str(ctx, user))

async def balance_str(ctx, user: discord.Member = None):
    if user is None:
        user_id = str(ctx.author.id)
    else:
        user_id = str(user.id)

    ensure_user_initialized(user_id)

    user_balance = db[user_id]
    return (
        f"**Balance**\n`Purse: ${user_balance['purse']}`\n`Bank: ${user_balance['bank']}`"
    )


bot.load_extension('cogs.casino')

try:
    bot.run(os.getenv('TOKEN'))
except Exception as err:
    raise err