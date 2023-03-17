import asyncio
import json

import discord
from discord import app_commands
from discord.ext import commands

from src.extras.FzSocket import FzSocket
from src.extras.posts import fz_login_post, fz_start_post
from src.extras.settingsSelector import SettingsSelectorView

def write_json(new_data, filename='./src/cogs/data.json'):
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
        guilds = self.bot.guilds
    
    guilds = [1080882268731621376]

    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    #@app_commands.guilds(guilds)
    async def _connect(self, ctx: discord.Interaction):

        await ctx.response.defer(ephemeral=True)
        data = json.load(open('./src/cogs/data.json'))
        token = data[str(ctx.guild.id)]['token']
        channelid = data[str(ctx.guild.id)]['channelid']
        logchannelid = data[str(ctx.guild.id)]['logchannelid']
        version = data[str(ctx.guild.id)]['version']
        save = data[str(ctx.guild.id)]['save']
        requireAdmin = data[str(ctx.guild.id)]['requireAdmin']

        if not ctx.user.guild_permissions.administrator:
            if requireAdmin == "Yes":
            	return await ctx.edit_original_response(content="You do not have permission to use this command", view=None)
        
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
                chan = self.bot.get_channel(int(channelid))
                await chan.send(f"Server started at `{ip}`")
                log = self.bot.get_channel(int(logchannelid))
                await log.send(f"IP: {ip}, launchid: {launchId}")
    
    @app_commands.command(name="settings", description="Connect to Factorio Zone Servers")
    #@app_commands.guilds(guilds)
    async def _settings(self, ctx:discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        if not ctx.user.guild_permissions.administrator:
            return await ctx.edit_original_response(content="You do not have permission to use this command", view=None)
        data = json.load(open('./src/cogs/data.json'))
        token = data[str(ctx.guild.id)]['token']
        channelid = data[str(ctx.guild.id)]['channelid']
        logchannelid = data[str(ctx.guild.id)]['logchannelid']
        requireAdmin = data[str(ctx.guild.id)]['requireAdmin']
        socket = FzSocket(ctx.guild.id)
        socket_task = asyncio.create_task(socket.connect())
        await ctx.edit_original_response(content="Let me pull up the settings information", view=None)
        respo = await fz_login_post(await socket.get_secret(), token)
        if respo is not None:
            regions = await socket.get_regions()
            saves = await socket.get_saves()
            versions = await socket.get_versions()
            settingsView = SettingsSelectorView(regions, saves, versions)
            await ctx.edit_original_response(content=f"Select the settings", view=settingsView)
            await settingsView.wait()
            data = {
                f"{ctx.guild.id}": {
                    "token": token,
                    "channelid": channelid,
                    "logchannelid": logchannelid,
                    "save": str(settingsView.selected_save),
                    "version": str(settingsView.selected_version),
                    "region": str(settingsView.selected_region),
                    "requireAdmin": requireAdmin
                }
            }
            write_json(data)
            await ctx.edit_original_response(content="Settings saved")
        socket_task.cancel()





async def setup(bot):
    await bot.add_cog(FzCommands(bot))
