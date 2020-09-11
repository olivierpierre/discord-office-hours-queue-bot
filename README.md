# Discord Office Hours Queue Bot

Discord is great for office hours, however with large group it can be hard to
maintain the order of arrival of students so that they can be helped in the
correct sequence by the instructor.

This is a very simple bot for discord written in python, allowing to maintain
an order of arrival for students. Upon arriving in the server the students start
a private conversation with the bot and use the following commands:

- `!joinq` to join the queue
- `!status` to enquire for their position in the queue (0 being the first
  position)
- `!leaveq` to leave the queue

The instructor/TAs also interract with the bot in private chat with these
commands:

- `!popq` to select the next student to see (automatically dequeues the
  student)
- `!clearq-yes-I-am-sure` to clear the queue
- `!viewq` to print the entire queue

## Installation

Dependencies:

Python3 as well as the discord library:
```shell
pip3 install -U discord.py
```

Once your discord server is set up, get a token following these instructions:
https://github.com/Tyrrrz/DiscordChatExporter/wiki/Obtaining-Token-and-Channel-IDs

Write the token in a file named `settings.json` in the local folder, see for
example `settings-sample.json`. Finally launch the bot as follows:

```shell
./bot.py
```

Obviously, the bot will only answers when it runs.


