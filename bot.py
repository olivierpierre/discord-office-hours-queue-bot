#!/usr/bin/python3

import os
import sys
import json
import discord

TOKEN = ""
QUEUE = []
GUILD = None

# Read options
try:
    with open('settings.json') as f:
        data = json.load(f)
        TOKEN = data["token"]
except FileNotFoundError as e:
    print("Cannot find settings.json, exiting...")
    sys.exit(-1)

client = discord.Client()

@client.event
async def on_ready():
    global GUILD

    if len(client.guilds) > 1 or len(client.guilds) < 1:
        print("Error regarding the number of servers...")
        sys.exit(-1)

    GUILD = client.guilds[0]
    print(f"{client.user} connected to Discord, on server " f"{GUILD.name}")

@client.event
async def on_message(message, pass_context=True):
    if message.author == client.user:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return

    msg = message.content.lower()

    if msg == '!joinq':
        if message.author.id not in QUEUE:
            QUEUE.append(message.author.id)
            await message.channel.send("OK, I added you to the queue! Your "\
                    "current position is: " + str(QUEUE.index(message.author.id)))
        else:
            await message.channel.send("You were already in the queue, your "\
                    "current position is: " + str(QUEUE.index(message.author.id)))

    elif msg == "!leaveq":
        if message.author.id in QUEUE:
            QUEUE.remove(message.author.id)
            await message.channel.send("OK, I removed you from the queue")
        else:
            await message.channel.send("You are not in the queue")

    elif msg == "!status":
        if message.author.id in QUEUE:
            await message.channel.send("Your position is: " +
                    str(QUEUE.index(message.author.id)))
        else:
            await message.channel.send("You are not in the queue")

    elif msg == "!popq":
        member = GUILD.get_member(message.author.id)
        authorized = False
        for role in member.roles:
            if role.name == "TA":
                authorized = True
        if authorized:
            if len(QUEUE) > 0:
                student = GUILD.get_member(QUEUE.pop(0))
                await message.channel.send("The next student is: " +
                        student.mention)
            else:
                await message.channel.send("Queue empty!")
        else:
            await message.channel.send("Sorry this command is only for TAs or"\
                    " the instructor")

    elif msg == "!clearq-yes-i-am-sure":
        member = GUILD.get_member(message.author.id)
        authorized = False
        for role in member.roles:
            if role.name == "TA":
                authorized = True
        if authorized:
            QUEUE.clear()
            await message.channel.send("Queue cleared")
        else:
            await message.channel.send("Sorry this command is only for TAs or"\
                    " the instructor")

    else:
        await message.channel.send("Sorry, I didn't get that... the available"\
                " commands are:\n"
                "`!joinq` to join the queue\n"\
                "`!status` to query your current position in the queue\n"\
                "`!leaveq` to leave the queue\n"\
                "`!popq` to get the first student in the queue "\
                "(instructor/TAs only)\n"\
                "`!clearq-yes-I-am-sure` to clear the queue "\
                "(instructor/TAs only)\n")


client.run(TOKEN)
