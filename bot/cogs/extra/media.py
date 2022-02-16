import yt_dlp
import os
import subprocess
import discord
import asyncio
import re
import aiohttp
import aiofiles.os
from nextcord.ext import commands
from env_var import env


class mediastuff(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def _youtube_results(self, query: str):
        try:
            headers = {"user-agent": "nanobot/3.0"}
            async with self.session.get(
                "https://www.youtube.com/results", params={"search_query": query}, headers=headers
            ) as r:
                result = await r.text()
            yt_find = re.findall(r"{\"videoId\":\"(.{11})", result)
            url_list = []
            for track in yt_find:
                url = f"https://www.youtube.com/watch?v={track}"
                if url not in url_list:
                    url_list.append(url)
        except Exception as e:
            url_list = [f"Something went terribly wrong! [{e}]"]
        return url_list

    @commands.command(name="youtube", alias=["yt"])
    async def youtube(self, ctx, *, query: str):
        """Search on Youtube."""
        result = await self._youtube_results(query)
        if result:
            await ctx.reply(result[0])
        else:
            await ctx.reply("Nothing found. Try again later.")

    @commands.command(name="ytdl", alias=["youtubedl", "ydl"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ytdl(self, ctx, query: str = None, convert: str = "video"):

        # Example video(s): http://www.youtube.com/watch?v=BaW_jenozKc
        #                   http://www.youtube.com/watch?v=jNQXAC9IVRw
        #                   https://youtu.be/khK_afMwAdA
        #
        # Btw, this script is incredibly garbage and doesn't work very well. When a user tries to use [p]ytdl, the whole bot will stop and wait until the download / upload is finished.

        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(query, download=False)
            video_id = info_dict.get("id", None)

        dlpath = "'temp/%(id)s.%(ext)s'"
        usage = f"{env.prefix}ytdl 'https://youtube.com/...' video / audio (default: video)"
        if not query:
            await ctx.reply(f"No YouTube URL found.\n```{usage}```")
        else:
            if convert == 'video':
                media_format = 'webm'
                opts = f'--recode-video {media_format}'
            elif convert == 'audio':
                media_format = 'mp3'
                opts = f'-x --audio-format {media_format}'
            elif convert == 'opus':
                media_format = 'opus'
                opts = f'-x --audio-format {media_format}'
            else:
                await ctx.reply(f"Invalid usage.\n```{usage}```")

            if not os.path.exists('temp'):
                os.mkdir('temp')

            # a pretty unsafe way of doing it, but yt_dlp doesn't support async io
            # i cant think of a better way to do this.
            try:
                subprocesspipe = asyncio.subprocess.PIPE
                child = await asyncio.create_subprocess_shell(
                    f"python3 -m yt_dlp --max-filesize 350M -f 22/18/5/36 --no-playlist {opts} --break-on-existing --no-exec -o {dlpath} {query}",
                    stderr=subprocesspipe,
                    stdout=subprocesspipe
                )
                msg = await ctx.reply(f"Downloading <{query}>...")
                stdout, stderr = await child.communicate()
            except Exception as e:
                await msg.edit(f"```{e}```")

            exitcode = child.returncode
            vidfile = f"{video_id}.{media_format}"
            deletemsg = await msg.delete()

            if exitcode == 0:
                try:
                    await ctx.reply(file=discord.File(f"temp/{vidfile}"))
                    deletemsg
                except Exception as e:
                    await ctx.reply(f"```{e}```")
                    deletemsg
            else:
                await msg.reply(f"Something went wrong. ```{exitcode}```")
            # remove the file after a certain amount of time (in this case, 14400 seconds is 4 hours)
            await asyncio.sleep(14400)
            if os.path.exists(f"temp/{vidfile}"):
                await aiof.os.remove(f"temp/{vidfile}")

    @commands.command(name="animalfact")
    async def animal_fact(self, ctx: commands.Context, URL="https://some-random-api.ml/animal/"):
        async with request("GET", URL, headers={}) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.reply(data["fact"])
            else:
                await ctx.reply(f"API returned a {response.status} status")


def setup(bot: commands.Bot):
    bot.add_cog(mediastuff(bot))