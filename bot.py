#!/usr/bin/python3

import os
import sys
import json
import discord

TOKEN = ""
QUEUE = []

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
    if len(client.guilds) > 1 or len(client.guilds) < 1:
        print("Error regarding the number of servers...")
        sys.exit(-1)

    guild = client.guilds[0]
    print(f"{client.user} connected to Discord, on server " f"{guild.name}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    if msg == '!joinq':
        if message.author not in QUEUE:
            QUEUE.append(message.author)
            await message.channel.send("OK, I added you to the queue! Your "\
                    "current position is: " + str(QUEUE.index(message.author)))
        else:
            await message.channel.send("You were already in the queue, your "\
                    "current position is: " + str(QUEUE.index(message.author)))

    elif msg == "!leaveq":
        if message.author in QUEUE:
            QUEUE.remove(message.author)
            await message.channel.send("OK, I removed you from the queue")
        else:
            await message.channel.send("You are not in the queue")

    elif msg == "!status":
        if message.author in QUEUE:
            await message.channel.send("Your position is: " + str(QUEUE.index(message.author)))
        else:
            await message.channel.send("You are not in the queue")

    else:
        await message.channel.send("Sorry, I didn't get that... the available commands are:")

client.run(TOKEN)
