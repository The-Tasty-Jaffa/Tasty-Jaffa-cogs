iimport discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import bcrypt

#Created by The Tasty Jaffa
#A lot of people have been asking for password channels in uservoice feed
#So I made this

#******************WARNING*******************
#
#WARNING: This will be CPU intensive :WARNING
#
#******************WARNING*******************

#If writing "Warning" 4 times and yet you didn't get the message...

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
        
        prv_channel = await self.bot.start_private_message(ctx.message.author)
        await self.bot.send_message(prv_channel, "Enter Password")
        password = await self.bot.wait_for_message(channel=prv_channel, timeout=30)
        if password.content is not None:
            if auth==True:
                if bcrypt.checkpw(password.content, self.storage[channel.id]):
                    if isinstance(channel.type, type(discord.ChannelType.text)):
                        perms = discord.PermissionOverwrite(read_messages=True)
                        await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)
                    elif isinstance(channel.type, type(discord.ChannelType.voice)):
                        perms = discord.PermissionOverwrite(connect=True)
                        await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)
                        
                else:
                    await self.bot.send_message(prv_channel, "That is not correct")
                    
            elif auth == False:
                if len(password.content) <= 30 or len(password.content) >= 5:
                    try:
                        defualt_role = ctx.message.server.default_role

                        if isinstance(channel.type, type(discord.ChannelType.text)):
                            perms = discord.PermissionOverwrite(read_messages=True)
                            await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                            perms = discord.PermissionOverwrite(read_messages=False)
                            await self.bot.edit_channel_permissions(channel, defualt_role, perms)
                            
                        elif isinstance(channel.type, type(discord.ChannelType.voice)):
                            perms = discord.PermissionOverwrite(connect=True)
                            await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                            perms = discord.PermissionOverwrite(connect=False)
                            await self.bot.edit_channel_permissions(channel, defualt_role, perms)

                        self.storage[channel.id] = bcrypt.hashpw(password.content, bcrypt.gensalt())
                    
                        dataIO.save_json("data/Tasty/pswdchannels/storage.json", self.storage)
                        await self.bot.send_message(prv_channel, "Password set!")
                            
                    except:
                        await self.bot.send_message(prv_channel, "An error occured... Make sure I have the right permissions")
                    
                else:
                    await self.bot.send_message(prv_channel, "password is the wrong length `Needs to be between 5 and 30 charractors")

        else:
            await self.bot.send_message(prv_channel, "You took to long!")
    

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def SetPassword(self, ctx, channel_id):
        channel = self.bot.get_channel(channel_id)
        
        if channel is not None:
            await self.Pswd(ctx,channel,auth=False)

        else:
            await self.bot.send_message(ctx.message.channel, "Channel not found!")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def RemovePassword(self, ctx, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)

            if isinstance(channel.type, type(discord.ChannelType.text)):
                perms = discord.PermissionOverwrite(read_messages=True)
                await self.bot.edit_channel_permissions(channel, ctx.message.server.default_role, perms)

            elif isinstance(channel.type, type(discord.ChannelType.voice)):
                perms = discord.PermissionOverwrite(connect=True)
                await self.bot.edit_channel_permissions(channel, ctx.message.server.default_role, perms)

            del self.storage[channel.id]
            dataIO.save_json("data/Tasty/pswdchannels/storage.json", self.storage)

        except discord.Forbidden:
            await self.bot.send_message(ctx.message.channel, "Humm... I wasn't able to do that...")

        except:
            await self.bot.send_message(ctx.message.channel,"Channel not found! Make sure to use the ID")

    @commands.command(pass_context=True)
    async def EnterPassword(self, ctx, channel_id):
        channel = self.bot.get_channel(channel_id)
        
        if channel is not None:
            await self.Pswd(ctx,channel,auth=True)

        else:
            await self.bot.send_message(ctx.message.channel, "Channel not found!")
          
            
def setup(bot):
    print("\n Warning you are using a CPU intensive cog --> pswdchannel")
    n = PswdChannels(bot)
    bot.add_cog(n)
