import discord
import os
import time
import random
from random import randint
import gspread
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

from discord.ext import commands, tasks
from discord import guild, embeds, Embed, InteractionResponse
from discord.utils import get
intents = discord.Intents.all()
bot_activity = discord.Game(name = "with your feelings")
client = commands.Bot(command_prefix = '$', intents = intents, case_insensitive = True, activity = bot_activity, help_command = None)

googleacc1 = gspread.service_account(filename = "timer-bot-extras-2821494ca615.json") # replace with the service account for the bot in googles apis (https://docs.gspread.org/en/latest/oauth2.html)
# bot1sheet = googleacc1.open_by_url("https://docs.google.com/spreadsheets/d/13Xs8NhG2cgAbnLG8gxJ0NTrCv9IqlFZZ6Q2b5k24jTA/edit#gid=0")
# bot1ws1 = bot1sheet.get_worksheet(0) # main sheet

bot1sheet2 = googleacc1.open_by_url("https://docs.google.com/spreadsheets/d/1cI6bFQPT9XB5M5Ip4s4YHYBEGdHpNK2zGsjnxgcpSUc/edit#gid=0")
bot1ws2 = bot1sheet2.get_worksheet(0) # quote sheet

# this is wintellectuals guild id
quoteguild = [771477838796161024]

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("you made an error in the command arguments")
        print(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("there is a required section missing in this command")
        print(error)
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("command failed to run")
        print(error)
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRole):
        await ctx.send("you do not have the required role to run this command. you need the LootCouncil role")
    else:
        await ctx.send("bruh idk what u did but it aint right")
        raise error




# gyze wake up new quote bot
# instead of writing to a google sheet (terrible) we are going to write to a csv file which will be in the same format as the google sheet (im great i know)
# formatting is as follows: quoteid, quote, author, quoter, timestamp
# in the quote, will need to double quote stuff to make sure it is read correctly
# quote files are called quotes_{guildid}.csv

@client.command()
async def addquote(ctx, quote, author):
    """Adds a quote to the quote list for the server"""
    if ctx.guild.id not in quoteguild:
        # put quote in file
        # if the file has no rows, write the header
        # get the quote id by getting the last row and adding 1
        # write the quote to the file
        # send a message saying the quote has been added
        quoteid = -1
        with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
            filelines = f.readlines()
            quoteid = len(filelines)
        with open(f'quotes_{ctx.guild.id}.csv', 'a+') as f:
            filelines = f.readlines()
            if os.stat(f'quotes_{ctx.guild.id}.csv').st_size == 0:
                f.write('quoteid,quote,author,quoter,timestamp\n')
            # put the quote in "" so that it is read correctly in the csv
            quote = f'"{quote}"'
            f.write(f'{quoteid},{quote},{author},{str(ctx.author)},{int(time.time())}\n')
        await ctx.send(f'Quote added: {quote} - {author} by {ctx.author} with an id of {quoteid}')
        return

    quoteid = int(bot1ws2.col_values(1)[-1]) + 1
    body = [quoteid, quote, author, str(ctx.author), int(time.time())]
    bot1ws2.append_row(body)
    await ctx.send(f'Quote added: {quote} - {author} by {ctx.author} with an id of {quoteid}')

@client.command()
async def getquote(ctx, quoteid):
    """Gets a quote from the quote list for the server by the quotes id"""
    if ctx.guild.id not in quoteguild:
        # get the quote from the file
        # check if the file exists
        # if it does, read the file and get the quote by the id
        # send the quote
        try:
            with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
                filelines = f.readlines()
                for line in filelines:
                    if line.split(',')[0] == quoteid:
                        quoteinfo = line.split(',')
                        quote = quoteinfo[1]
                        quoteauthor = quoteinfo[2]
                        embtosend = discord.Embed(title = quote, description = quoteauthor, color = discord.Color.blue())
                        embtosend.set_footer(text = f'Quote id: {quoteid} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(quoteinfo[4])))} by {quoteinfo[3]}')
                        await ctx.send(embed = embtosend)
                        return
                await ctx.send("Quote not found")
        except FileNotFoundError:
            await ctx.send("No quotes have been added to this server")
    quoteids = bot1ws2.col_values(1)
    quoteindex = quoteids.index(quoteid) + 1
    quoteinfo = bot1ws2.row_values(quoteindex)
    quote = quoteinfo[1]
    quoteauthor = quoteinfo[2]
    embtosend = discord.Embed(title = quote, description = quoteauthor, color = discord.Color.blue())
    embtosend.set_footer(text = f'Quote id: {quoteid} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(quoteinfo[4])))} by {quoteinfo[3]}')
    await ctx.send(embed = embtosend)

@client.command()
async def getrandom(ctx):
    """Gets a quote from the quote list for the server by the quotes id"""
    if ctx.guild.id not in quoteguild:
        # get the quote from the file
        # check if the file exists
        # if it does, read the file and get the quote by the id
        # send the quote
        try:
            with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
                filelines = f.readlines()
                quoteid = randint(1, len(filelines)) - 1
                #quoteid is not the quoteid of the quote, its the index of the line in the file so:
                quoteid = filelines[quoteid].split(',')[0]
                for line in filelines:
                    if line.split(',')[0] == quoteid:
                        quoteinfo = line.split(',')
                        quote = quoteinfo[1]
                        quoteauthor = quoteinfo[2]
                        embtosend = discord.Embed(title = quote, description = quoteauthor, color = discord.Color.blue())
                        embtosend.set_footer(text = f'Quote id: {quoteid} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(quoteinfo[4])))} by {quoteinfo[3]}')
                        await ctx.send(embed = embtosend)
                        return
                await ctx.send("Quote not found fsr")
        except FileNotFoundError:
            await ctx.send("No quotes have been added to this server")
    quoteinfo = bot1ws2.row_values(randint(2, len(bot1ws2.col_values(1))))
    quote = quoteinfo[1]
    quoteauthor = quoteinfo[2]
    embtosend = discord.Embed(title = quote, description = quoteauthor, color = discord.Color.blue())
    embtosend.set_footer(text = f'Quote id: {quoteinfo[0]} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(quoteinfo[4])))} by {quoteinfo[3]}')
    await ctx.send(embed = embtosend)

@client.command()
async def quotesby(ctx, person):
    """Gets quotes from the quote list for the server by the quotes id"""
    if ctx.guild.id not in quoteguild:
        try:
            with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
                filelines = f.readlines()
                quotesadded = 0
                pagenum = 1
                for line in filelines:
                    if quotesadded % 25 == 0:
                        if quotesadded != 0:
                            await ctx.send(embed = embed)
                            pagenum += 1
                        embed = discord.Embed(title = f'Quotes by {person} - Page {pagenum}', color = discord.Color.blue())
                    if person.lower() in line.split(',')[2].lower():
                        quoteinfo = line.split(',')
                        quote = quoteinfo[1]
                        if quotesadded % 25 == 24:
                            embed.add_field(name = f'{quote}', value = f'- {quoteinfo[2]}, Quoted by {quoteinfo[3]}. ID: {quoteinfo[0]}', inline = False)
                        else:
                            embed.add_field(name = f'{quote}', value = f'- {quoteinfo[2]}, Quoted by {quoteinfo[3]}. ID: {quoteinfo[0]} \n ‎', inline = False)
                        quotesadded += 1
                await ctx.send(embed = embed)
        except FileNotFoundError:
            await ctx.send("No quotes have been added to this server")
        return
    quotequoters = bot1ws2.col_values(4)
    quoteauthors = bot1ws2.col_values(3)
    quotestrings = bot1ws2.col_values(2)
    zipped = list(zip(quoteauthors, quotestrings, quotequoters))
    quotesadded = 0
    pagenum = 1
    for i in range(len(zipped)):
        if quotesadded % 25 == 0:
            if quotesadded != 0:
                await ctx.send(embed = embed)
                pagenum += 1
            embed = discord.Embed(title = f'Quotes by {person} - Page {pagenum}', color = discord.Color.blue())
        if person.lower() in zipped[i][0].lower():
            quote = zipped[i][1]
            if quotesadded % 25 == 24:
                embed.add_field(name = f'{quote}', value = f'- {zipped[i][0]}, Quoted by {zipped[i][2]}. ID: {i}', inline = False)
            else:
                embed.add_field(name = f'{quote}', value = f'- {zipped[i][0]}, Quoted by {zipped[i][2]}. ID: {i} \n ‎', inline = False)
            quotesadded += 1
    await ctx.send(embed = embed)

@client.command()
async def quotesheet(ctx):
    """Sends the link to the quote sheet"""
    if ctx.guild.id not in quoteguild:
        await ctx.send("This server doesnt have a quote sheet \n All the quotes are stored in a local file instead \n use getquotefile to return the file contents")
        return
    await ctx.send("https://docs.google.com/spreadsheets/d/1cI6bFQPT9XB5M5Ip4s4YHYBEGdHpNK2zGsjnxgcpSUc/edit#gid=0")

@client.command()
async def getquotefile(ctx):
    """Sends the quote file"""
    if ctx.guild.id not in quoteguild:
        try:
            with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
                await ctx.send(file = discord.File(f, filename = f'quotes_{ctx.guild.id}.csv'))
        except FileNotFoundError:
            await ctx.send("No quotes have been added to this server")
    else:
        await ctx.send("This server has a quote sheet \n Use quotesheet to get the link to the sheet")

@client.command()
async def deletequote(ctx, quoteid):
    if ctx.guild.id not in quoteguild:
        try:
            with open(f'quotes_{ctx.guild.id}.csv', 'r') as f:
                filelines = f.readlines()
                for line in filelines:
                    if line.split(',')[0] == quoteid:
                        quoteindex = filelines.index(line)
                        break
                filelines.pop(quoteindex)
            with open(f'quotes_{ctx.guild.id}.csv', 'w') as f:
                f.writelines(filelines)
            await ctx.send(f'Quote with id {quoteid} has been deleted')
            return
        except FileNotFoundError:
            await ctx.send("No quotes have been added to this server")
    quoteids = bot1ws2.col_values(1)
    quoteindex = quoteids.index(quoteid) + 1
    bot1ws2.delete_rows(quoteindex)
    await ctx.send(f'Quote with id {quoteid} has been deleted')

@client.command()
async def help(ctx):
    await ctx.send("""```​No Category:
    addquote  Adds a quote to the quote list for the server
    getquote  Gets a quote from the quote list for the server by the quotes id
    getrandom Gets a random quote from the quote list for the server
    quotesby  Gets quotes from the quote list for the server by the quotes id
    quotesheet  Sends the link to the quote sheet (wintellectuals only)
    deletequote  Deletes a quote from the quote list for the server by the quotes id```""")
    return
    # await ctx.send("""```​No Category:
  #addquote  Adds a quote to the quote list for the server
  #bt        display the bloodthorn leaderboard
  #dino      display the dino leaderboard
  #gele      display the gelebron leaderboard
  #help      Shows this message
  #lbadd     Adds a name to the leaderboard
  #lbremove  Removes a name from the leaderboard
  #lbswap    Swaps two names on the leaderboard
  #mord      display the mordris leaderboard
  #necro     display the necro leaderboard
  #prot      display the prot leaderboard

# Type $help command for more info on a command.
# You can also type $help category for more info on a category.```""")


# @client.command()
# async def creedmoor(ctx):
#     await ctx.send("my names <@396099210073735178> and I lose aggro on everything")
# 
# @client.command()
# async def precise(ctx):
#     await ctx.send("stop longshotting BT")
# 
# @client.command()
# async def baleno(ctx):
#     await ctx.send("pls buy more chests")
# 
# @client.command()
# async def dza(ctx):
#     selected = random.choice(["make another discord bot", "deez", "when are my wins getting mailed?", "Vote aO for DG"])
#     await ctx.send(selected)
# 
# @client.command()
# async def silent(ctx):
#     await ctx.send("ima request that just to have it")
# 
# @client.command()
# async def metro(ctx):
#     selected = random.choice(["off to play golf", "bring magic trimmings", "tótem"])
#     await ctx.send(selected)
# 
# @client.command()
# async def whatsapp(ctx):
#     await ctx.send("needs 80 rare bt bands")
# 
# @client.command()
# async def viagra(ctx):
#     await ctx.send("My names <@701251992517083247> and I take this cause I have ED")
# 
# @client.command()
# async def kiwi(ctx):
#     await ctx.send("LGBT rights")
# 
# @client.command()
# async def slayer(ctx):
#     await ctx.send("unox due in 2 hours 14 minutes")
# 
# @client.command()
# async def winston(ctx):
#     await ctx.send("dead bot")
# 
# @client.command()
# async def falk(ctx):
#     await ctx.send("you have all that gear and STILL LOSE")
# 
# @client.command()
# async def zpk(ctx):
#     await ctx.send("where did he go <:pepehands:1180525430747439194>")
# 
# @client.command()
# async def quarter(ctx):
#     selected = random.choice(["have a coffee", "drop the ego", "i'd die on that hill", "full greed or death", "WATER", "that's wart", "polish off some beers", "it's good to be king", "buying giga rare companion bird 10m", "get useful chap", "top tier gear is reserved for those who do above the bare minimum"])
#     await ctx.send(selected)
# 
# @client.command()
# async def shelly(ctx):
#     await ctx.send("When are you levelling?")
# 
# @client.command()
# async def muds(ctx):
#     await ctx.send("I miss my girlfriend")
# 
# @client.command()
# async def gear(ctx):
#     await ctx.send("top tier gear is reserved for those who do above the bare minimum")
# 
# @client.command()
# async def darkmage(ctx):
#     await ctx.send("please put some trousers on")
# 
# @client.command()
# async def trevor(ctx):
#     await ctx.send("My names <@384425186889433088> and I ruined Epona and Rhiannon now I’m here to ruin Fingal")
# 
# @client.command()
# async def sonic(ctx):
#     await ctx.send("My names <@447941383790133259> and when I grow up, I want to be just like Quarter")
# 
# @client.command()
# async def paranoid(ctx):
#     await ctx.send("Greed is good")
#     await ctx.send("https://tenor.com/view/greedy-cake-slice-of-cake-chocolate-cake-cut-gif-17838337")
# 
# @client.command()
# async def rejuvenation(ctx):
#     await ctx.send("sorry guys I'm at the gym I can't make reset")

# @client.command(name = 'lbadd')
# @commands.has_role("LootCouncil")
# async def lbadd(ctx, boss, name):
#     """Adds a name to the leaderboard"""
#     if boss.lower() == 'mord':
#         mordboard = bot1ws1.col_values(2)
#         mordboard.pop(0)
#         if len(mordboard) < 10:
#             bot1ws1.update_cell(len(mordboard)+2, 2, name)
#             await ctx.send(f"{name} has been added to the Mordris leaderboard at position {len(mordboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
#     elif boss.lower() == 'necro':
#         necroboard = bot1ws1.col_values(4)
#         necroboard.pop(0)
#         if len(necroboard) < 10:
#             bot1ws1.update_cell(len(necroboard)+2, 4, name)
#             await ctx.send(f"{name} has been added to the Necro leaderboard at position {len(necroboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
#     elif boss.lower() == 'prot':
#         protboard = bot1ws1.col_values(6)
#         protboard.pop(0)
#         if len(protboard) < 10:
#             bot1ws1.update_cell(len(protboard)+2, 6, name)
#             await ctx.send(f"{name} has been added to the Proteus leaderboard at position {len(protboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
#     elif boss.lower() == 'gele':
#         geleboard = bot1ws1.col_values(8)
#         geleboard.pop(0)
#         if len(geleboard) < 10:
#             bot1ws1.update_cell(len(geleboard)+2, 8, name)
#             await ctx.send(f"{name} has been added to the Gelebron leaderboard at position {len(geleboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
#     elif boss.lower() == 'bt':
#         btboard = bot1ws1.col_values(10)
#         btboard.pop(0)
#         if len(btboard) < 10:
#             bot1ws1.update_cell(len(btboard)+2, 10, name)
#             await ctx.send(f"{name} has been added to the Bloodthorn leaderboard at position {len(btboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
#     elif boss.lower() == 'dino':
#         dinoboard = bot1ws1.col_values(12)
#         dinoboard.pop(0)
#         if len(dinoboard) < 10:
#             bot1ws1.update_cell(len(dinoboard)+2, 12, name)
#             await ctx.send(f"{name} has been added to the Dino leaderboard at position {len(dinoboard)+1}")
#         else:
#             await ctx.send("The leaderboard is full")
# 
# 
# @client.command(name = 'lbremove')
# @commands.has_role("LootCouncil")
# async def lbremove(ctx, boss, name):
#     """Removes a name from the leaderboard"""
#     if boss.lower() == 'mord':
#         mordboard = bot1ws1.col_values(2)
#         mordboard.pop(0)
#         if name in mordboard:
#             bot1ws1.update_cell(mordboard.index(name)+2, 2, '')
#             for i in range(mordboard.index(name)+1, len(mordboard)):
#                 bot1ws1.update_cell(i+1, 2, mordboard[i])
#             bot1ws1.update_cell(len(mordboard)+1, 2, '')
#             await ctx.send(f"{name} has been removed from the Mordris leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Mordris leaderboard")
#     elif boss.lower() == 'necro':
#         necroboard = bot1ws1.col_values(4)
#         necroboard.pop(0)
#         if name in necroboard:
#             bot1ws1.update_cell(necroboard.index(name)+2, 4, '')
#             for i in range(necroboard.index(name)+1, len(necroboard)):
#                 bot1ws1.update_cell(i+1, 4, necroboard[i])
#             bot1ws1.update_cell(len(necroboard)+1, 4, '')
#             await ctx.send(f"{name} has been removed from the Necro leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Necro leaderboard")
#     elif boss.lower() == 'prot':
#         protboard = bot1ws1.col_values(6)
#         protboard.pop(0)
#         if name in protboard:
#             bot1ws1.update_cell(protboard.index(name)+2, 6, '')
#             for i in range(protboard.index(name)+1, len(protboard)):
#                 bot1ws1.update_cell(i+1, 6, protboard[i])
#             bot1ws1.update_cell(len(protboard)+1, 6, '')
#             await ctx.send(f"{name} has been removed from the Proteus leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Proteus leaderboard")
#     elif boss.lower() == 'gele':
#         geleboard = bot1ws1.col_values(8)
#         geleboard.pop(0)
#         if name in geleboard:
#             bot1ws1.update_cell(geleboard.index(name)+2, 8, '')
#             for i in range(geleboard.index(name)+1, len(geleboard)):
#                 bot1ws1.update_cell(i+1, 8, geleboard[i])
#             bot1ws1.update_cell(len(geleboard)+1, 8, '')
#             await ctx.send(f"{name} has been removed from the Gelebron leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Gelebron leaderboard")
#     elif boss.lower() == 'bt':
#         btboard = bot1ws1.col_values(10)
#         btboard.pop(0)
#         if name in btboard:
#             bot1ws1.update_cell(btboard.index(name)+2, 10, '')
#             for i in range(btboard.index(name)+1, len(btboard)):
#                 bot1ws1.update_cell(i+1, 10, btboard[i])
#             bot1ws1.update_cell(len(btboard)+1, 10, '')
#             await ctx.send(f"{name} has been removed from the Bloodthorn leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Bloodthorn leaderboard")
#     elif boss.lower() == 'dino':
#         dinoboard = bot1ws1.col_values(12)
#         dinoboard.pop(0)
#         if name in dinoboard:
#             bot1ws1.update_cell(dinoboard.index(name)+2, 12, '')
#             for i in range(dinoboard.index(name)+1, len(dinoboard)):
#                 bot1ws1.update_cell(i+1, 12, dinoboard[i])
#             bot1ws1.update_cell(len(dinoboard)+1, 12, '')
#             await ctx.send(f"{name} has been removed from the Dino leaderboard")
#         else:
#             await ctx.send(f"{name} is not on the Dino leaderboard")
# 
# @client.command(name = 'lbswap')
# @commands.has_role("LootCouncil")
# async def lbswap(ctx, boss, name1, name2):
#     """Swaps two names on the leaderboard"""
#     if boss.lower() == 'mord':
#         mordboard = bot1ws1.col_values(2)
#         mordboard.pop(0)
#         if name1 in mordboard and name2 in mordboard:
#             bot1ws1.update_cell(mordboard.index(name1)+2, 2, name2)
#             bot1ws1.update_cell(mordboard.index(name2)+2, 2, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Mordris leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Mordris leaderboard")
#     elif boss.lower() == 'necro':
#         necroboard = bot1ws1.col_values(4)
#         necroboard.pop(0)
#         if name1 in necroboard and name2 in necroboard:
#             bot1ws1.update_cell(necroboard.index(name1)+2, 4, name2)
#             bot1ws1.update_cell(necroboard.index(name2)+2, 4, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Necro leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Necro leaderboard")
#     elif boss.lower() == 'prot':
#         protboard = bot1ws1.col_values(6)
#         protboard.pop(0)
#         if name1 in protboard and name2 in protboard:
#             bot1ws1.update_cell(protboard.index(name1)+2, 6, name2)
#             bot1ws1.update_cell(protboard.index(name2)+2, 6, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Proteus leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Proteus leaderboard")
#     elif boss.lower() == 'gele':
#         geleboard = bot1ws1.col_values(8)
#         geleboard.pop(0)
#         if name1 in geleboard and name2 in geleboard:
#             bot1ws1.update_cell(geleboard.index(name1)+2, 8, name2)
#             bot1ws1.update_cell(geleboard.index(name2)+2, 8, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Gelebron leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Gelebron leaderboard")
#     elif boss.lower() == 'bt':
#         btboard = bot1ws1.col_values(10)
#         btboard.pop(0)
#         if name1 in btboard and name2 in btboard:
#             bot1ws1.update_cell(btboard.index(name1)+2, 10, name2)
#             bot1ws1.update_cell(btboard.index(name2)+2, 10, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Bloodthorn leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Bloodthorn leaderboard")
#     elif boss.lower() == 'dino':
#         dinoboard = bot1ws1.col_values(12)
#         dinoboard.pop(0)
#         if name1 in dinoboard and name2 in dinoboard:
#             bot1ws1.update_cell(dinoboard.index(name1)+2, 12, name2)
#             bot1ws1.update_cell(dinoboard.index(name2)+2, 12, name1)
#             await ctx.send(f"{name1} and {name2} have been swapped on the Dino leaderboard")
#         else:
#             await ctx.send(f"Both {name1} and {name2} must be on the Dino leaderboard")
#     
# 
# @client.command(name = 'mord')
# async def mord(ctx):
#     """display the mordris leaderboard"""
#     mordboard = bot1ws1.col_values(2)
#     mordboard.pop(0)
#     embed = discord.Embed(title = "Mordris Leaderboard", color = discord.Color.blue())
#     for i in range(len(mordboard)):
#         embed.add_field(name = f"{i+1}. {mordboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)
# 
# @client.command(name = 'necro')
# async def necro(ctx):
#     """display the necro leaderboard"""
#     necroboard = bot1ws1.col_values(4)
#     necroboard.pop(0)
#     embed = discord.Embed(title = "Necro Leaderboard", color = discord.Color.blue())
#     for i in range(len(necroboard)):
#         embed.add_field(name = f"{i+1}. {necroboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)
# 
# @client.command(name = 'prot')
# async def prot(ctx):
#     """display the prot leaderboard"""
#     protboard = bot1ws1.col_values(6)
#     protboard.pop(0)
#     embed = discord.Embed(title = "Proteus Leaderboard", color = discord.Color.blue())
#     for i in range(len(protboard)):
#         embed.add_field(name = f"{i+1}. {protboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)
# 
# @client.command(name = 'gele')
# async def gele(ctx):
#     """display the gelebron leaderboard"""
#     geleboard = bot1ws1.col_values(8)
#     geleboard.pop(0)
#     embed = discord.Embed(title = "Gelebron Leaderboard", color = discord.Color.blue())
#     for i in range(len(geleboard)):
#         embed.add_field(name = f"{i+1}. {geleboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)
# 
# @client.command(name = 'bt')
# async def bt(ctx):
#     """display the bloodthorn leaderboard"""
#     btboard = bot1ws1.col_values(10)
#     btboard.pop(0)
#     embed = discord.Embed(title = "Bloodthorn Leaderboard", color = discord.Color.blue())
#     for i in range(len(btboard)):
#         embed.add_field(name = f"{i+1}. {btboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)
# 
# @client.command(name = 'dino')
# async def dino(ctx):
#     """display the dino leaderboard"""
#     dinoboard = bot1ws1.col_values(12)
#     dinoboard.pop(0)
#     embed = discord.Embed(title = "Dino Leaderboard", color = discord.Color.blue())
#     for i in range(len(dinoboard)):
#         embed.add_field(name = f"{i+1}. {dinoboard[i]}", value = f"", inline = False)
#     await ctx.send(embed = embed)



client.run(TOKEN)