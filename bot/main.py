print("Importing packages")
try:
    import time
    # Log the amount of time it takes to start the bot
    start_time = time.time()
    import asyncio
    from aiohttp import request
    from art import text2art
    from nextcord.ext import commands
    from console import console
    from rich import print, inspect
    from env_var import env
    import discord
    import json
    import logging
    import sys
    import os
    import platform
    import psutil
except ImportError as e:
    print(f"Broken or missing module: {e}")
    exit()


author = "coff3e"
name = env.botname
version = env.version
sourcepage = env.sourcepage
prefix = env.prefix

console.system(f"System:\t")
inspect(platform.uname())
osplatform = platform.system()
if osplatform != "Linux":
    console.warn(
        f"{osplatform.capitalize()} ISN'T TESTED. USE AT YOUR OWN RISK."
    )


if env.activitytype == 'playing':
    activitytype = discord.ActivityType.playing
elif env.activitytype == 'watching':
    activitytype = discord.ActivityType.watching
elif env.activitytype == 'listening':
    activitytype = discord.ActivityType.listening


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
activity = discord.Activity(name=env.botactivity, type=activitytype)


console.log(
    f"Starting nanobot ({name})"
)


# Bot params + info
bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
    intents=intents,
    help_command=None,
    activity=activity,
    allowed_mentions=discord.AllowedMentions(
        users=True,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
        replied_user=True,  # Whether to ping on replies to messages
    ),
)


def returnln(returns: int = 1):
    for x in range(returns):
        ln = sys.stdout.write("\033[F")


def cogservice(filepath):
    basic_cogs = ['errorhandler',
                  'botmgr',
                  'help',
                  'cogs.testing.admin',
                  'cogs.base.basecmd',
                  'cogs.base.pkgmgr'
                  ]
    console.log(f"Finding {filepath}")
    returnln()
    if os.path.exists(filepath):
        console.success(f"Found {filepath}")
        with open(filepath, 'r') as service:
            cogsenabled = service.read().split()
    else:
        cogsenabled = basic_cogs
        console.error(
            f"'{filepath}' wasn't found. Create the file with basic cogs? (Y/n)")
        useri = input('>> ')
        if 'y' in useri:
            if not os.path.exists('config'):
                os.mkdir('config')
            f = open('config/service.txt', 'w')
            for cogs in cogsenabled:
                f.write(f"{cogs}\n")
    service.close()
    for cogs in cogsenabled:
        try:
            cog_start_time = time.time()
            console.log(f"loading {cogs}")
            bot.load_extension(cogs)
            cog_end_time = time.time()
            # time.sleep(2)
            returnln()
            console.success(
                f"loaded {cogs} ({round((cog_end_time - cog_start_time) * 1000)}ms)")
        except Exception as e:
            sys.stdout.write("\033[F")
            console.error(f"loading {cogs} failed:\n({e})")


async def botupdate(URL: str = "https://raw.githubusercontent.com/get-coff3e/nanobot/testing/bot/version.json"):
    async with request("GET", URL, headers={}) as response:
        if env.updatemsg:
            if response.status == 200:
                data = await response.json(content_type=None)
                newversion = data["botversion"]
                if newversion != version:
                    print(
                        f"Newest nanobot version on github doesn't match the one installed. It may be outdated, please consider updating.\n\t\t\tQueried URL:\t\t{URL}\n\t\t\tInstance Version:\t{ version}\n\t\t\tLatest found:\t\t{newversion}\n\t\t\tIf you would like to disable this message, set [bold orange]UPDATEMSG[/] to False in your environment")
            else:
                print("Couldn't reach github")


@bot.event
async def on_ready():
    console.success('Connection made!\n')
    # nanobot startup ascii art
    console.nanostyle(
        text2art(name, 'random')
    )

    if "DEV" in version:
        print(f"[red]\nVersion: {version}[/]")
        print(f"[bold red]! ! !   DEV VERSION   ! ! ![/]\n")
        print(f"[red]Report bugs to: {sourcepage}[/]")
    else:
        print(f"[white]\nVersion: {version}[/]")

# Discord API User info + prefix
    print("\n----------------------------------------")
    print()
    print(f'[magenta]Logged in as [/][underline]{bot.user}[/] ({bot.user.id})')
    print(f'[magenta]Prefix: {prefix}[/]')
    print()
    print("----------------------------------------\n")

# printing list of joined guilds and its data
    console.botlog("Joined guilds:")
    num = 0
    joined = bot.guilds
    count = []
    if len(joined) > 1:
        for guilds in joined:
            try:
                count.append(guilds)
                print(f'\t\t\t\t{len(count)} - {guilds}')
            except Exception as e:
                console.error(e)
        console.botlog(f'Total joined guilds: {len(joined)}')
    else:
        console.botlog(f"Not joined into any guilds. Invite the bot using ...")

    if intents.members:
        users = bot.users
# Uncomment these lines below to print out all users the bot sees. Otherwise, it will only show you how many there are.
        #console.botlog(f"Found users:")
        # try:
        #    print(users)
        # except Exception as e:
        #    console.error(e)
        console.botlog(f"Total unique users found: {len(users)}")

# load cogs from cogservice function
    cogservice('config/service.txt')

# printing the time it took to start the bot
    end_time = time.time()
    console.log(
        f"Took {round((end_time - start_time) * 1000)}ms ({round((end_time - start_time) * 1)}s) to start-up"
    )

    await botupdate()


if __name__ == "__main__":
    # Loading TOKEN from .env
    console.botlog("Attempting to connect to Discord API")
    try:
        bot.run(env.token)
    except Exception as e:
        console.error(e)
