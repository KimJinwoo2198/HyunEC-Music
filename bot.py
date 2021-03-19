import json
import time
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands


class MusicBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = dict()

    async def play_music(self, ctx, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:4321/getytinfo?{quote(query)}"
            ) as resp:
                data = json.loads(await resp.text())
        music = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                source=data["url"],
            ),
            volume=1.0,
        )
        self.players[ctx.guild.id] = {
            "channel": ctx.channel,
            "current": {"started": time.time(), "data": data},
            "queue": [],
            "voice_client": ctx.voice_client,
            "volume": 1.0,
        }
        if not ctx.voice_client.is_playing():
            ctx.voice_client.play(
                music, after=lambda _e: self.after_music_finished(ctx.guild.id)
            )
            await ctx.reply(
                f"`{data['info']['title']}` 노래를 지금 재생할게요!",
            )
        else:
            self.players[ctx.guild.id]["queue"].append(data)
            await ctx.reply(
                f"`{data['info']['title']}` 노래를 대기열에 추가했습니다.",
            )
        return data

    def after_music_finished(self, guild_id: int):
        if self.players[guild_id]["queue"]:
            data = self.players[guild_id]["queue"].pop(0)
            music = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    source=data["url"],
                ),
                volume=self.players[guild_id]["volume"],
            )
            self.players[guild_id]["voice_client"].play(
                music, after=lambda _e: self.after_music_finished(guild_id)
            )
            self.loop.create_task(
                self.players[guild_id]["channel"].send(
                    f"`{data['info']['title']}` 노래를 지금 재생할게요!"
                )
            )
        else:
            try:
                self.players[guild_id]["voice_client"].stop()
                self.loop.create_task(
                    self.players[guild_id]["voice_client"].disconnect()
                )
                del self.players[guild_id]
            except KeyError:
                pass
