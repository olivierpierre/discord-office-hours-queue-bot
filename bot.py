#!/usr/bin/python3

import os
import sys
import json
import asyncio
import discord

NICKNAME = "QueueBot"
TOKEN = ""
QUEUE = []
NOTIFY = []
GUILD = None
LOCK = asyncio.Lock()

# Read token from settings.json
try:
    with open('settings.json') as f:
        data = json.load(f)
        TOKEN = data["token"]
except FileNotFoundError as e:
    print("Cannot find settings.json, exiting...")
    sys.exit(-1)

client = discord.Client()

# Get a member from his id
# If get_member does not work it means the member is not cached and we need to
# use fetch_member to get it
async def get_member(member_id):
    member = GUILD.get_member(member_id)
    if member == None:
        member = await GUILD.fetch_member(member_id)
    return member

# Check if a member is privileged (TA/instructor) or not (student)
def is_privileged(member):
    for role in member.roles:
        if role.name == "TA":
            return True
    return False

# Notify all instructors/TAs waiting for the queue to become non empty
async def notify():
    while NOTIFY:
        user_id = NOTIFY.pop()
        m = await get_member(user_id)
        await m.send("Hi there, this is " + NICKNAME + ", someone just "\
                "joined the queue!")

@client.event
async def on_ready():
    global GUILD

    # There should be only 1 server the bot is connected to
    if len(client.guilds) > 1 or len(client.guilds) < 1:
        print("Error regarding the number of servers...")
        sys.exit(-1)

    GUILD = client.guilds[0]
    print(f"{client.user} connected to Discord, on server " f"{GUILD.name}")
    print("Hit [ctrl + c] to exit")


@client.event
async def on_message(message, pass_context=True):
    # Not sure about concurrency so let's serialize eveything for now
    async with LOCK:
        # Don't have the bot reply to itself
        if message.author == client.user:
            return

        # The bot only answers to private messages
        if not isinstance(message.channel, discord.DMChannel):
            return

        msg = message.content.lower()

        # !joinq: typed by a student to join the queue
        if msg == '!joinq':
            if message.author.id not in QUEUE:
                QUEUE.append(message.author.id)
                if len(QUEUE) == 1:
                    await GUILD.me.edit(nick=NICKNAME + "*")
                    await notify()
                await message.channel.send("OK, I added you to the queue! Your "\
                        "current position is: " + str(QUEUE.index(message.author.id)))
            else:
                await message.channel.send("You were already in the queue, your "\
                        "current position is: " + str(QUEUE.index(message.author.id)))

        # !leaveq: typed by a student to leave the queue
        elif msg == "!leaveq":
            if message.author.id in QUEUE:
                QUEUE.remove(message.author.id)
                if len(QUEUE) == 0:
                    await GUILD.me.edit(nick=NICKNAME)
                await message.channel.send("OK, I removed you from the queue")
            else:
                await message.channel.send("You are not in the queue")

        # !status: typed by a student to query his position in the queue
        elif msg == "!status":
            if message.author.id in QUEUE:
                await message.channel.send("Your position is: " +
                        str(QUEUE.index(message.author.id)))
            else:
                await message.channel.send("You are not in the queue")

        # !popq: typed by TA/instructor to pop from the queue the next student to see
        elif msg == "!popq":
            member = await get_member(message.author.id)
            if is_privileged(member):
                if len(QUEUE) > 0:
                    student = await get_member(QUEUE.pop(0))
                    if len(QUEUE) == 0:
                        await GUILD.me.edit(nick=NICKNAME)
                    await message.channel.send("The next student is: " +
                            student.mention)
                else:
                    await message.channel.send("Queue empty!")
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        # !clearq-yes-i-am-sure: TA/instructor clears the queue. Voluntarily long
        # so we don't clear it by mistake
        elif msg == "!clearq-yes-i-am-sure":
            member = await get_member(message.author.id)
            if is_privileged(member):
                QUEUE.clear()
                await GUILD.me.edit(nick=NICKNAME)
                await message.channel.send("Queue cleared")
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        # !viewq: TA/instructor prints the entire queue
        elif msg == "!viewq":
            member = await get_member(message.author.id)
            if is_privileged(member):
                msg = ""
                if not QUEUE:
                    msg += "Queue empty!\n"
                for student_id in QUEUE:
                    student = await get_member(student_id)
                    msg += str(QUEUE.index(student_id)) + ". "
                    msg += student.mention + "\n"
                await message.channel.send(msg)
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        # !notify: TA/instructor requests to be notified once the queue
        # becomes non empty
        elif msg == "!notify":
            member = await get_member(message.author.id)
            if is_privileged(member):
                if len(QUEUE) == 0:
                    NOTIFY.append(message.author.id)
                    await message.channel.send("Alright, I'll ping you when "\
                            "someone enters the queue")
                else:
                    await message.channel.send("Queue is already non empty!")
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        else:
            await message.channel.send("Sorry, I didn't get that... the available"\
                    " commands are:\n"
                    "`!joinq` to join the queue\n"\
                    "`!status` to query your current position in the queue (0: "\
                        "first)\n"\
                    "`!leaveq` to leave the queue\n"\
                    "`!popq` to get the first student in the queue "\
                    "(instructor/TAs only)\n"\
                    "`!clearq-yes-I-am-sure` to clear the queue "\
                    "(instructor/TAs only)\n"\
                    "`!viewq` to print the queue (instructor/TAs only)")

# For some reason this needs to be below on_ready/on_message
client.run(TOKEN)
