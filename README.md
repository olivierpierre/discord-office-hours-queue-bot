# Discord Office Hours Queue Bot

Discord is great for office hours, however with large groups it can be hard to
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
privileged commands:

- `!popq` to select the next student to see (automatically dequeues the
  student)
- `!viewq` to print the entire queue
- `!notify` when the queue is empty, to have the bot privately message the
  instructor/TA once someone joins the queue
- `!notify-always` works similarly to `!notify`, but does not need to be
  relaunched each time a signal is sent, i.e. it will always signal the
  instructor/TA when someone joins an empty queue
- `!clearq-yes-I-am-sure` to clear the queue

You need to setup a role named `TA` in your discord server and give it to the
person(s) you want to be able to use the privileged commands. A Discord server
template with the correct setup is available here:
https://discord.new/6tXKxc93fsm5.

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

Obviously, the bot will only answer when it runs. Don't forget to setup a role
named `TA` on your server and give it to the people supposed to use the
privileged commands.


