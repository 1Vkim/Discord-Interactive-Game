import discord
from replit import db
from discord.ext import commands
import random

# Casino cog class that will handle all casino-related commands and events
class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event listener that triggers when the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user}')
        self.initialize_casino()

    # Function to initialize the casino if it doesn't exist in the database
    def initialize_casino(self):
        if 'casino' not in db.keys():
            db['casino'] = {'bank': 10000}

    # Command to place a bet in the casino
    @commands.command()
    async def casino(self, ctx, amount: int, prediction: int):
        user_id = str(ctx.author.id)
        self.ensure_user_initialized(user_id)

        # Check if amount and prediction are provided
        if amount is None:
            await ctx.send("Add amount and Prediction number(2-12)")
        else:
            # Check if the prediction is within the valid range
            if prediction < 2 or prediction > 12:
                await ctx.send("Prediction must be a number between 2 and 12.")
                return

            # Check if the user has enough money to place the bet
            if db[user_id]['purse'] < amount and db[user_id]['bank'] < amount:
                await ctx.send("You do not have enough money to place this bet.")
                return

            # Deduct the bet amount from the user's purse or bank
            if db[user_id]['purse'] >= amount:
                db[user_id]['purse'] -= amount
            else:
                db[user_id]['bank'] -= amount

            # Roll the dice
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total = dice1 + dice2

            await ctx.send(f"Rolling dice... You predicted {prediction}. The dice rolled {dice1} and {dice2}, for a total of {total}.")

            # Determine if the user won or lost the bet
            if total == prediction:
                winnings = amount * prediction
                db[user_id]['purse'] += winnings
                await ctx.send(f"Congratulations! You won {winnings}!")
            else:
                db['casino']['bank'] += amount
                await ctx.send(f"Sorry, you lost. The money goes to the casino.")

    # Function to ensure the user's data is initialized in the database
    def ensure_user_initialized(self, user_id):
        if user_id not in db['users'] or db['users'][user_id] is None:
            db['users'][user_id] = {'bank': 0, 'purse': 0, 'items': {}, 'pets': {}}
        if 'items' not in db['users'][user_id]:
            db['users'][user_id]['items'] = {}

    # Error handler for the casino command
    @casino.error
    async def casino_error(self,ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: /casino <amount> <prediction>")
        
# Function to add the cog to the bot
def setup(bot):
    bot.add_cog(Casino(bot))

