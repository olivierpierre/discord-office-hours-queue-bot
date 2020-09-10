#!/usr/bin/python3

import os
import sys
import json
import discord

TOKEN = ""

# Read options
try:
    with open('settings.json') as f:
        data = json.load(f)
        TOKEN = data["token"]
except FileNotFoundError as e:
    print("Cannot find settings.json, exiting...")
    sys.exit(-1)

print("Token: " + TOKEN)


client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
