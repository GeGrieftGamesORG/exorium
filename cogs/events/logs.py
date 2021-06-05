import discord, config, time, aiohttp, psutil, platform
from collections import Counter
from discord.ext import commands
from datetime import datetime
from utils import default
from bot import get_prefix

class logs(commands.Cog, name="Logs"):
    def __init__(self, bot):
        self.bot = bot

    async def bot_check(self, ctx):
        if ctx.author == await self.bot.fetch_user(809057677716094997):  # bluewy
            return True  # even if gets blacklisted can't be blocked from the bot

        try:
            blacklist_check = self.bot.blacklist[ctx.author.id]
            if blacklist_check:
                return False  # they're blacklisted.
        except Exception:
            return True

    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(f"{datetime.now().__format__('%a %d %b %y, %H:%M')} - {ctx.guild.name} | {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.database.execute("SELECT * FROM blacklist WHERE id = %s", [guild.id])
        results = self.bot.database.fetchall()

        if not results:
            log = self.bot.get_channel(839963272114602055)
            owner = await self.bot.fetch_user(guild.owner_id)
            owner = str(owner)

            l = discord.Embed(color=discord.Color.green(), title="New guild joined")
            l.set_author(name=guild, icon_url=guild.icon_url)
            l.set_footer(text=f"Now in {len(self.bot.guilds)} guilds")
            l.description = f"""
Guild **{guild}** ({guild.id})
Owner: **{owner}** ({guild.owner_id})
Created on **{default.date(guild.created_at)}**
Approximately **{guild.member_count}** members
**{len(guild.text_channels)}** text & **{len(guild.voice_channels)}** voice channels
Icon url: **[Click here]({guild.icon_url})** 
"""

            return await log.send(guild.id, embed=l)

        else:
            print(f"{guild} is blacklisted for {blacklist_check}")
            return await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log = self.bot.get_channel(839963272114602055)
        owner = await self.bot.fetch_user(guild.owner_id)
        owner = str(owner)

        l = discord.Embed(color=discord.Color.red(), title="Old guild left")
        l.set_author(name=guild, icon_url=guild.icon_url)
        l.set_footer(text=f"Now in {len(self.bot.guilds)} guilds")
        l.description = f"""
        Guild **{guild}** ({guild.id})
        Owner: **{owner}** ({guild.owner_id})
        Created on **{default.date(guild.created_at)}**
        Approximately **{guild.member_count}** members
        **{len(guild.text_channels)}** text & **{len(guild.voice_channels)}** voice channels
        Icon url: **[Click here]({guild.icon_url})** 
        """

        await log.send(embed=l)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """ Tries to re-run a command when a message gets edited! """
        if after.author.bot is True or before.content == after.content:
            return
        prefixes = commands.when_mentioned_or('exo ', 'Exo ', 'e!')(self.bot, after)
        if after.content.startswith(tuple(prefixes)):
            ctx = await self.bot.get_context(after)
            msg = await self.bot.invoke(ctx)

def setup(bot):
    bot.add_cog(logs(bot))
