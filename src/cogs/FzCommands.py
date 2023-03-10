import asyncio
import json

import discord
from discord import app_commands
from discord.ext import commands

from src.extras.FzSocket import FzSocket
from src.extras.database import get_tokens
from src.extras.posts import fz_login_post, fz_start_post
from src.extras.settingsSelector import SettingsSelectorView
from src.extras.tokenSelector import TokenSelectorView


class FzCommands(commands.Cog):
    """Class for the Factorio Zone cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    @app_commands.guilds(1053562951497420871)
    async def _connect(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        # check if the user has any tokens
        tokens = ""
        if not tokens:
            await ctx.edit_original_response(content="You don't have any tokens, please user /add-token to add one")
        else:
            socket = FzSocket(ctx.user.id)
            socket_task = asyncio.create_task(socket.connect())
            respo = await fz_login_post(await socket.get_secret(), tokens)
            if respo is not None:
                regions = await socket.get_regions()
                saves = 1
                versions = "1.1.74"
                await ctx.edit_original_response(content=f"Starting the server", view=None)
                response = await fz_start_post(socket.visit_secret, regions,
                                               versions, saves)
                if response is not None:
                    ip = await socket.get_ip()
                    launchId = await socket.get_launch_id()
                    await ctx.edit_original_response(content=f"Server started at `{ip}`\nLaunch Id: {launchId}",
                                                    view=None)
                    chan = self.bot.get_channel(1053750097843847339)
                    await chan.send(f"Server started at `{ip}`\nLaunch Id: {launchId}")

async def setup(bot):
    await bot.add_cog(FzCommands(bot))
