import discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import bcrypt

#Created by The Tasty Jaffa
#Code reviewed by samwho (and a few others in "Programming Discussions" discord server)
#A lot of people have been asking for password channels in uservoice feed
#So I made this

#WARNING: This can be CPU intensive


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
        
    async def Pswd(self, ctx, channel, auth): # This deals with the passwords
        
        prv_channel = await self.bot.start_private_message(ctx.message.author)
        await self.bot.send_message(prv_channel, "Enter Password")
        password = await self.bot.wait_for_message(channel=prv_channel, timeout=120, author=ctx.message.author)
        await self.bot.send_message(prv_channel, "Password Entered\n")

        if password.content is None:
            await self.bot.send_message(prv_channel, "Sorry but I cannot accept empty passwords")
            return

        if auth is True: #Authenticates passwords
            if bcrypt.checkpw(password.content, self.storage[channel.id]):
                
                if isinstance(channel.type, type(discord.ChannelType.text)):
                    perms = discord.PermissionOverwrite(read_messages=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                elif isinstance(channel.type, type(discord.ChannelType.voice)):
                    perms = discord.PermissionOverwrite(connect=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)
                
                await self.bot.send_message(prv_channel, "Correct password entered")
                    
            else:
                await self.bot.send_message(prv_channel, "You did not enter a correct password")
                
        elif auth is False: #Sets passwords

            if len(password.content) >= 64 or len(password.content) <= 5:
                await self.bot.send_message(prv_channel, "The password is the wrong length, It must be longer than 5 charactors and shorter than 64")
                return

            try: # No need for this - Check permissions instead and return if false.
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
                    
            except discord.Forbidden:
                #Since passwords can only be set by admins, asking for permissions should be fine
                await self.bot.send_message(prv_channel, "Make sure I have the right permissions! (permissions required: Manage channels, Manage roles")

    @commands.command(pass_context=True, name="setpassword")
    @checks.admin_or_permissions(manage_channels=True)
    async def set_password(self, ctx, channel_id):
        """Allows you to set a password for that channel"""
        channel = self.bot.get_channel(channel_id)
        
        if channel is not None:
            await self.Pswd(ctx, channel, auth=False)

        else:
            await self.bot.send_message(ctx.message.channel, "Channel not found! Make sure to use the channel ID")

    @commands.command(pass_context=True, name="removepassword")
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_password(self, ctx, channel_id):
        """Allows you to remove a password from that channel"""
        try: # If channel is none: return; again check for permissions
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
            await self.bot.send_message(ctx.message.channel, "Humm... I wasn't able to do that... Check my discord permissions.")

        except:
            await self.bot.send_message(ctx.message.channel,"Channel not found! Make sure to use the channel ID")


    @commands.command(pass_context=True, name="enterpassword",)
    async def enter_password(self, ctx, channel_id):
        """Allows you to enter a password for that channel"""
        channel = self.bot.get_channel(channel_id)
        
        if channel is not None:
            await self.Pswd(ctx,channel,auth=True)

        else:
            await self.bot.send_message(ctx.message.channel, "Channel not found! Make sure to use the channel ID")
          
            
def setup(bot):
    print("\nWARNING you are using the CPU intensive cog --> pswdchannel\n")
    n = PswdChannels(bot)
    bot.add_cog(n)
