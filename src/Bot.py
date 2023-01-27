import logging
import asyncio
import os
import sys
from datetime import datetime
from sys import gettrace

import discord
from discord.ext.commands import Bot
from prettytable import PrettyTable

from src.extras.database import start_db


class FzBot(Bot):
    def __init__(self):
        self.active_sockets = []
        super().__init__(command_prefix="==", intents=discord.Intents.all())
        if gettrace() is None:
            self.debug_guild = discord.Object(id=1053562951497420871)
        else:
            self.debug_guild = discord.Object(id=1053562951497420871)

    async def on_ready(self):
        logging.info("Bot is ready")
        table = PrettyTable()
        table.field_names = ["Name", "Value"]
        table.add_row(["Bot Name", self.user.name])
        table.add_row(["Bot ID", self.user.id])
        table.add_row(["Discord Version", discord.__version__])
        table.add_row(["Python Version", "{}.{}.{}".format(*sys.version_info)])
        table.add_row(["Start Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        table.align["Name"] = "l"
        table.align["Value"] = "l"
        logging.info(f"\n{table}")
        await start_db()
        logging.info("Database started")
        if gettrace():
            await self.load_extension(f"src.devCogs.Events")
            await self.load_extension(f"src.devCogs.FzDevCommands")
        else:
            await self.load_extension(f"src.cogs.FzCommands")
        await asyncio.sleep(5)
        await self.tree.sync(guild=self.debug_guild)
        logging.info("Command tree synced")
