import json
import logging
import os
import subprocess

try:
    import discord
    from discord.ext import commands
except ModuleNotFoundError:
    cmd = subprocess.Popen(("python" "setup.py"), stderr=subprocess.PIPE)
    cmd.stdout.read()

from bot import MusicBot

with open("config.json") as f:
    config = json.load(f)

bot = MusicBot(
    command_prefix=config["prefixs"],
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, replied_user=False
    ),
    owner_ids=config["owner_ids"],
)

discord_log = logging.getLogger("discord")
discord_log.addHandler(logging.FileHandler("discord.log"))
discord_log.setLevel(logging.INFO)

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


@bot.event
async def on_ready():
    log.info(f"{bot.user} 클라이언트로 로그인했습니다.")
    bot.load_extension("jishaku")
    for filename in os.listdir("cogs"):
        if not filename.startswith("__"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            log.info(f"'{filename}' 파일을 불러왔습니다.")


@bot.event
async def on_command(ctx):
    log.info(
        f"{ctx.author}: {ctx.message.content} | {ctx.guild if ctx.guild else 'DM'} | {ctx.channel if ctx.guild else ''} {ctx.message.created_at}"
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.MaxConcurrencyReached):
        await ctx.send("해당 명령어는 현재 실행중입니다! 기존 명령어가 끝날 때 까지 기다려주세요!")
    else:
        await ctx.send(f"```\n{error}```")


subprocess.Popen(
    (".\server.exe"),
)
bot.run(config["token"])
