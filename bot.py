#!/usr/bin/python3

import os
import sys
import json
import asyncio
import time
from datetime import datetime
import discord
import argparse

NICKNAME = "QueueBot"
TOKEN = ""
QUEUE = []
NOTIFY = []
NOTIFY_ALWAYS = []
GUILD = None
LOCK = asyncio.Lock()
LOGGING = False

parser = argparse.ArgumentParser(description="Discord office hours bot.")
parser.add_argument("-l", "--logging", help="Log queue state evolution",
        action="store_true")
parser.add_argument("-s", "--settings", help="Specify settings file "\
        "(default will be settings.json in the local directory)")
args = parser.parse_args()

if args.logging:
    LOGGING = args.logging

settings = "./settings.json"
if args.settings:
    settings = args.settings

# Load settings
try:
    with open(settings) as f:
        data = json.load(f)
        TOKEN = data["token"]
except FileNotFoundError as e:
    print("Cannot find file " + settings + ", exiting...")
    sys.exit(-1)

client = discord.Client()


def queue_empty():
    return (len(QUEUE) == 0)

# Clear the queue
async def clear_queue():
    QUEUE.clear()
    await GUILD.me.edit(nick=NICKNAME)
    if LOGGING:
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S: ") + "queue cleared")

# Pop a student from the queue
async def pop_from_queue():
    student = QUEUE.pop(0)
    if len(QUEUE) == 0:
        await GUILD.me.edit(nick=NICKNAME)
    if LOGGING:
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S: ") + str(student["id"]) + " popped")
    return student

# Add someone to the queue
async def add_to_queue(member_id):
    QUEUE.append({ "id" : member_id,
        "time" : time.time()})
    if len(QUEUE) == 1:
        await GUILD.me.edit(nick=NICKNAME + "*")
        await notify()
    if LOGGING:
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S: ") + str(member_id) + " joined")

# Remove someone from the queue
async def remove_from_queue(member_id):
    for m in QUEUE:
        if m["id"] == member_id:
            QUEUE.remove(m)
            break
    if len(QUEUE) == 0:
        await GUILD.me.edit(nick=NICKNAME)
    if LOGGING:
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S: ") + str(member_id) + " removed")

# Get the position of an id in the queue. Returns -1 if not present.
def get_position(member_id):
    for m in QUEUE:
        if m["id"] == member_id:
            return QUEUE.index(m)
    return -1

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
    for user in NOTIFY_ALWAYS:
        m = await get_member(user)
        await m.send("Hi there, this is " + NICKNAME + ", someone just "\
                "joined the queue!")

@client.event
async def on_ready():
    global GUILD

    # There should be only 1 server the bot is connected to
    if len(client.guilds) > 1 or len(client.guilds) < 1:
        print("Error: this bot is not connected to any server, or it is"\
                " connected to more than one server (currently "\
                "unsupported), exiting...")
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
            if get_position(message.author.id) == -1:
                await add_to_queue(message.author.id)
                await message.channel.send("OK, I added you to the queue! Your "\
                        "current position is: " + \
                        str(get_position(message.author.id)))
            else:
                await message.channel.send("You were already in the queue, your "\
                        "current position is: " + \
                        str(get_position(message.author.id)))

        # !leaveq: typed by a student to leave the queue
        elif msg == "!leaveq":
            if get_position(message.author.id) != -1:
                await remove_from_queue(message.author.id)
                await message.channel.send("OK, I removed you from the queue")
            else:
                await message.channel.send("You are not in the queue")

        # !status: typed by a student to query his position in the queue
        elif msg == "!status":
            if get_position(message.author.id) != -1:
                await message.channel.send("Your position is: " +
                        str(get_position(message.author.id)))
            else:
                await message.channel.send("You are not in the queue")

        # !popq: typed by TA/instructor to pop from the queue the next student to see
        elif msg == "!popq":
            member = await get_member(message.author.id)
            if is_privileged(member):
                if not queue_empty():
                    student = await pop_from_queue()
                    member = await get_member(student["id"])
                    # Compute time waiting
                    wait_time = time.time() - student["time"]
                    str_wait_time = \
                            datetime.utcfromtimestamp(wait_time).strftime('%Mm %Ss')
                    await message.channel.send("The next student is: " +
                            member.mention + " (waited for " + str_wait_time + ")")
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
                await clear_queue()
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
                for member in QUEUE:
                    # Compute time waiting
                    wait_time = time.time() - member["time"]
                    str_wait_time = "queued for " + \
                            datetime.utcfromtimestamp(wait_time).strftime('%Mm %Ss')
                    student = await get_member(member["id"])
                    msg += str(QUEUE.index(member)) + ". "
                    msg += student.mention + " (" + str_wait_time + ")\n"
                await message.channel.send(msg)
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        # !notify: TA/instructor requests to be notified once the queue
        # becomes non empty
        elif msg == "!notify":
            member = await get_member(message.author.id)
            if is_privileged(member):
                if queue_empty():
                    if message.author.id not in NOTIFY:
                        NOTIFY.append(message.author.id)
                    await message.channel.send("Alright, I'll ping you when "\
                            "someone enters the queue")
                else:
                    await message.channel.send("Queue is already non empty!")
            else:
                await message.channel.send("Sorry this command is only for TAs or"\
                        " the instructor")

        elif msg == "!notify-always":
            member = await get_member(message.author.id)
            if is_privileged(member):
                if message.author.id not in NOTIFY_ALWAYS:
                    NOTIFY_ALWAYS.append(message.author.id)
                    await message.channel.send("Alright, I'll always ping you "\
                            "when someone enters the queue")
                else:
                    NOTIFY_ALWAYS.remove(message.author.id)
                    await message.channel.send("I removed you from the "\
                            "always-notify list")
            else:
                await message.channel.send("Sorry this command is only for TAs"\
                        " or the instructor")

        else:
            await message.channel.send("Sorry, I didn't get that... "\
                    "the available commands are:\n"
                    "`!joinq` to join the queue\n"\
                    "`!status` to query your current position in the queue (0: "\
                        "first)\n"\
                    "`!leaveq` to leave the queue\n"\
                    "`!popq` to get the first student in the queue "\
                    "(instructor/TAs only)\n"\
                    "`!clearq-yes-I-am-sure` to clear the queue "\
                    "(instructor/TAs only)\n"\
                    "`!viewq` to print the queue (instructor/TAs only)\n"\
                    "`!notify` to get notified next time someone joins the "\
                    "queue (instructor/TA only)")

# For some reason this needs to be below on_ready/on_message
client.run(TOKEN)
