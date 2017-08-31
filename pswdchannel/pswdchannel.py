import discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import bycrypt, getpass

#Created by The Tasty Jaffa


class PswdChannels:
    def __init__(self, bot):
        self.bot = bot
    
        if not os.path.exists("data/Tasty/pswdchannels"):
            print("Creating data/Tasty/pswdchannels folder...")
            os.makedirs("data/Tasty/pswdchannels")


        if not dataIO.is_valid_json("data/Tasty/pswdchannels/storage.json"):
            print("Creating empty storage.json...")
            dataIO.save_json("data/Tasty/pswdchannels/storage.json", {})

        self.storage = dataIO.load_json("data/Tasty/pswdchannels/storage.json")
        
    async def Pswd(self, ctx, channel, auth):
        
        prv_channel = self.bot.start_private_message(ctx.message.author)
        if auth==True:
            password = await self.bot.wait_for_message(channel=prv_channel, timeout=10)
            if bcrypt.checkpw(password, self.storage[channel.id]):
                if self.bot.channel.type == "text":
                    perms = discord.PermissionsOverwrite(read_messages=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)
                elif self.bot.channel.type == "voice":
                    perms = discord.PermissionsOverwrite(connect=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)
            else:
                await self.bot.send_message(prv_channel, "That is not correct")
                
        elif auth == False:
            if len(password) <= 30 or len(password) >= 5:
                try:
                    defualt_role = await ctx.message.server.default_role
                    if self.bot.channel.type == "text":
                        perms = discord.PermissionsOverwrite(read_messages=False)
                        await self.bot.edit_channel_permissions(channel, defualt_role, perms)
                    elif self.bot.channel.type == "voice":
                        perms = discord.PermissionsOverwrite(connect=False)
                        await self.bot.edit_channel_permissions(channel, defualt_role, perms)

                self.storage[channel.id] = bcrypt.hashpw(password, bcrypt.gensalt())
                dataIO.save_json("data/Tasty/pswdchannels/storage.json", self.storage)
                await self.bot.send_message(prv_channel, "Password set!")
                
            else:
                await self.bot.send_message(prv_channel, "password is the wrong length `Needs to be between 5 and 30 charractors")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def SetPassword(self, ctx, channel_id):
        try:
            channel = await self.bot.get_channel(channel_id)
        except:
            await self.bot.send_message(ctx.message.channel,"Channel not found! Make sure to use the ID")

        if channel is not None:
            self.Pswd(ctx,channel,auth=False)

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def RemovePassword(self, ctx, channel_id):
        try:
            del self.storage[channel.id]
            dataIO.save_json("data/Tasty/pswdchannels/storage.json", self.storage)
        except:
            await self.bot.send_message(ctx.message.channel,"Channel not found! Make sure to use the ID")

    @commands.command(pass_context=True)
    async def EnterPassword(self, ctx, channel_id):
        try:
            channel = await self.bot.get_channel(channel_id)
        except:
            await self.bot.send_message(ctx.message.channel,"Channel not found! Make sure to use the ID")

        if channel is not None:
            self.Pswd(ctx,channel,auth=True)
          
            
def setup(bot):
    logger = logging.getLogger('aiohttp.client')
    logger.setLevel(50)  # Stops warning spam
    n = PswdChannels(bot)
    bot.add_cog(n)
