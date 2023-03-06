import asyncio
import json

import discord
from discord import app_commands
from discord.ext import commands

from src.extras.FzSocket import FzSocket
from src.extras.database import get_tokens
from src.extras.posts import fz_login_post, fz_start_post
from src.extras.settingsSelector import save
from src.extras.tokenSelector import TokenSelectorView

def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data.update(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

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
        data = json.load(open('data.json'))
        token = data[ctx.guild.id]['token']
        chanelid = data[ctx.guild.id]['chanelid']
        version = data[ctx.guild.id]['version']
        save = data[ctx.guild.id]['save']
        for guild_id, socket, socket_task in self.bot.active_sockets:
            if guild_id == ctx.guild.id:
                await ctx.edit_original_message(content="Ther server is already on!!!", view=None)
                return
        
        socket = FzSocket(ctx.guild.id)
        socket_task = asyncio.create_task(socket.connect())
        respo = await fz_login_post(await socket.get_secret(), token)
        if respo is not None:
            regions = await socket.get_regions()
            await ctx.edit_original_response(content=f"Starting the server", view=None)
            response = await fz_start_post(socket.visit_secret, regions, version, save)
            if response is not None:
                ip = await socket.get_ip()
                launchId = await socket.get_launch_id()
                await ctx.edit_original_response(content=f"Server started at `{ip}`\nLaunch Id: {launchId}", view=None)
                chan = self.bot.get_channel(chanelid)
                await chan.send(f"Server started at `{ip}`\nLaunch Id: {launchId}")
                self.bot.active_sockets.append((ctx.guild.id, socket, socket_task))
    
    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    @app_commands.guilds(1053562951497420871)
    async def _settings(self, ctx:discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        data = json.load(open('data.json'))
        token = data[ctx.guild.id]['token']
        channelid = data[ctx.guild.id]['channelid']
        for guild_id, socket, socket_task in self.bot.active_sockets:
            if guild_id == ctx.guild.id:
                socket = FzSocket(ctx.guild.id)
                socket_task = asyncio.create_task(socket.connect())
                await ctx.edit_original_message(content="Let me pull up the settings information", view=None)
                respo = await fz_login_post(await socket.get_secret(), token)
                if respo is not None:
                    regions = await socket.get_regions()
                    saves = await socket.get_saves()
                    versions = await socket.get_versions()
                    settingsView = SettingsSelectorView(regions, saves, versions)
                    await ctx.edit_original_message(content=f"Select the settings", view=settingsView)
                    await settingsView.wait()
                    data = {
                        f"{ctx.guild.id}": {
                            "token": token
                            "channelid": channelid
                            "save": str(settingsView.selected_save),
                            "version": str(settingsView.selected_version),
                            "region": str(settingsView.selected_region)
                        }
                    }
                    write_json(data)
                    await ctx.edit_original_message(content="Settings saved")
                socket_task.cancel()





async def setup(bot):
    await bot.add_cog(FzCommands(bot))
