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


client.run(TOKEN)