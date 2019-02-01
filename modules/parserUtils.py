from modules import CalendarApi, DateUtils, FormatUtils, contactUtils, botUtils
import re, os, random
calendar = CalendarApi.CalendarAPI()

bot = botUtils.Bot()
def getUser(userhandle , message):
    return message.server.get_member_named(userhandle)

def getName(message):
    name = message.author.name
    discriminator = message.author.discriminator
    return name + "#" + discriminator

def checkPermissions(message, client):
    if "Lennon" not in message.author.name:
        return False
    else:
        return True

async def reject(message, client):
        await client.add_reaction(message, "🇳")
        await client.add_reaction(message, "🇴")
        await client.add_reaction(message, "🅿")
        await client.add_reaction(message, "🇪")

async def addReact(message, client, msg, user):
        if msg[0] == True and msg[1] != "":
            statement = user.mention + " You have been added to the waitlist for this session, because you are in the " + msg[1]
            await client.add_reaction(message, "✔")
            await client.send_message(message.channel, statement)
        elif msg[0] == True and msg[1] == "":
            await client.add_reaction(message, "☑")
        elif msg[0] == False  and msg[1] == "Full":
            statement = user.mention + " The mission you're trying to join is full"
            await client.add_reaction(message, "❌")
            await client.send_message(message.channel, statement)
        elif msg[0] == False and msg[1] == "Double":
            statement = user.mention + " You're already in this mission. You cannot join twice"
            await client.add_reaction(message, "❌")
            await client.send_message(message.channel, statement)
        elif msg[0] == False and msg[1] == "Invalid":
            await client.add_reaction(message, "❌")
            statement = user.mention + " You did not use the correct format. Please review the correct format and try again. "
            await client.send_message(message.channel, statement)    
        elif msg[0] == False and msg[1] == "Missing":
            await client.add_reaction(message, "❌")
            statement = user.mention + " There is no session scheduled for the date and region you mentioned."
            await client.send_message(message.channel, statement)    
            
async def removeReact(message, client, msg, user):
        if msg[0] == False and msg[1] == "Invalid":
            await client.add_reaction(message, "❌")
            statement = user.mention + " You did not use the correct format. Please review the correct format and try again. "
            await client.send_message(message.channel, statement)    
        if msg[0] == False and msg[1] == "Empty":
            await client.add_reaction(message, "❌")
            statement = user.mention + " You are not in this mission. You cannot leave a mission you aren't in."
            await client.send_message(message.channel, statement)      
        if msg[0] == True:
            date = msg[1][0]
            region = msg[1][1]
            await client.add_reaction(message, "☑")      
            statement = user.mention + " You have been removed from the {region} session scheduled for {date}".format(region=region,date=date)
            await client.send_message(message.channel, statement)   
        
async def parseMessage(message, client):
    mentions = [x.name for x in message.mentions]
    
# we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if "Helper" not in mentions:
        return
    
    permissions = checkPermissions(message, client)
    
    # if message.mentions[0].nick == "Helper":
        # await client.send_message(message.channel, message.content)

    if message.content.startswith("!hello"):
        await client.send_message(message.channel, message.content)


    if "avail!" in message.content:
        if not permissions:
            await reject(message,client)
            return
        msg = bot.getAvailability(message)
        await client.send_message(message.channel, msg)
    
    if "prnt!" in message.content:
        if not permissions:
            await reject(message,client)
            return
        msg = bot.printSessions(message)
        await client.send_message(message.channel, msg)
    
    if "create!" in message.content:
        if not permissions:
            await reject(message,client)
            return
        msg = bot.createSession(message)
        if msg == True:
            await client.add_reaction(message, "☑")
        else:
            await client.add_reaction(message, "❌")
            await client.send_message(message.channel, msg)
    
    if "add!" in message.content:
        name = getName(message)
        msg = bot.addUser(message,name)
        user = getUser(name, message)
        print(user.mention)
        await addReact(message, client,msg,user)

    if "addmem!" in message.content:
        if not permissions:
            await reject(message,client)
            return
        contactobj = contactUtils.getContacts()
        tempMessage = re.sub(".*addmem! ","", message.content)
        messageArray = [x.strip() for x in tempMessage.split(",")]
        name = messageArray[0]
        userhandle = contactobj[name][1]
        user = getUser(userhandle, message)
        del messageArray[0]
        msg = bot.addUser(message,name, True)
        await addReact(message, client,msg,user)

    if "remove!" in message.content:
        name = getName(message)
        msg = bot.removeUser(message,name)
        user = getUser(name, message)
        await removeReact(message,client,msg, user)

    if "removemem!" in message.content:
        if not permissions:
            await reject(message,client)
            return
        contactobj = contactUtils.getContacts()
        tempMessage = re.sub(".*removemem! ","", message.content)
        messageArray = [x.strip() for x in tempMessage.split(",")]
        name = messageArray[0]
        userhandle = contactobj[name][1]
        user = getUser(userhandle, message)
        del messageArray[0]
        msg = bot.removeUser(message,name, True)
        await removeReact(message,client,msg, user)

    if "whereami?" in message.content:
        name = getName(message)
        msg = bot.getSessionsByUser(message, name)
        # await client.send_message(message.author, "Test")
