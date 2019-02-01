import discord
from modules import botUtils, parserUtils, CalendarApi, contactUtils
import re, os, random
from importlib import reload
TOKEN = contactUtils.getToken()
client = discord.Client()
@client.event
async def on_message(message):
    if "restart!" in message.content:
        mentions = [x.name for x in message.mentions]
        if "Helper" in mentions: 
            reload(botUtils)
            reload(parserUtils)
            reload(CalendarApi)
            await client.add_reaction(message, "👍")
    else:
        await parserUtils.parseMessage(message,client)
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)