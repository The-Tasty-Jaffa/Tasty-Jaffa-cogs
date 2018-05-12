import discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
try:
    import bcrypt, pymongo
    from pymongo import MongoClient
except Exception as e:
    raise RuntimeError("Make sure to have the right modules installed... Try `pip3 install pymongo` and `pip3 install py-bcrypt`")

try:
    client =  MongoClient()
    db = client["red-discordbot-managedchannels"]
except:
    raise RuntimeError("Could not load Database - Check the GIT docs for more info.")

#Created by The Tasty Jaffa
#Code reviewed by samwho (and a few others in "Programming Discussions" discord server)
#A lot of people have been asking for password channels in uservoice feed
#So I made this

#WARNING: This can be CPU intensive


class PswdChannels:
    def __init__(self, bot):
        self.bot = bot
        
    async def Pswd(self, ctx, channel, auth): # This deals with the passwords
        
        prv_channel = await self.bot.start_private_message(ctx.message.author)
        await self.bot.send_message(prv_channel, "Enter Password")
        password = await self.bot.wait_for_message(channel=prv_channel, timeout=120, author=ctx.message.author)
        await self.bot.send_message(prv_channel, "Password Entered\n")

        if password.content is None:
            await self.bot.send_message(prv_channel, "Sorry but I cannot accept empty passwords")
            return

        if auth is True: #Authenticates passwords
            try:
                if bcrypt.checkpw(password.content.encode('utf-8'), db.users.find_one({'CHANNEL':channel.id})['PSWD']): # Checks entered password against stored password
                    # Causes Type error if no password is set for that channel

                    if isinstance(channel.type, type(discord.ChannelType.text)): #text channel
                        perms = discord.PermissionOverwrite(read_messages=True)
                        await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                    elif isinstance(channel.type, type(discord.ChannelType.voice)): #voice channel
                        perms = discord.PermissionOverwrite(connect=True)
                        await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                    await self.bot.send_message(prv_channel, "Correct password entered")

                else:
                    await self.bot.send_message(prv_channel, "You did not enter a correct password")
                    
            except TypeError:
                await self.bot.send_message(prv_channel,"That channel does not have a password set!")
                
        elif auth is False: #Sets passwords

            if len(password.content) >= 64 or len(password.content) <= 5:
                await self.bot.send_message(prv_channel, "The password is the wrong length, It must be longer than 5 charactors and shorter than 64")
                return

            try:
                defualt_role = ctx.message.server.default_role
                
                #Text channel
                if isinstance(channel.type, type(discord.ChannelType.text)):
                    perms = discord.PermissionOverwrite(read_messages=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                    perms = discord.PermissionOverwrite(read_messages=False)
                    await self.bot.edit_channel_permissions(channel, defualt_role, perms)
                
                #Voice channels
                elif isinstance(channel.type, type(discord.ChannelType.voice)):
                    perms = discord.PermissionOverwrite(connect=True)
                    await self.bot.edit_channel_permissions(channel, ctx.message.author, perms)

                    perms = discord.PermissionOverwrite(connect=False)
                    await self.bot.edit_channel_permissions(channel, defualt_role, perms)
                
                #adds pswd and channel to DB
                db.users.insert_one({'CHANNEL':channel.id, 'PSWD':bcrypt.hashpw(password.content.encode('utf-8'), bcrypt.gensalt())})
                await self.bot.send_message(prv_channel, "Password set!")
                    
            except discord.Forbidden:
                #Ask for admins for correct permissions since only admins can set pswd
                await self.bot.send_message(prv_channel, "An error occured... Make sure I have the right permissions! (permissions required: Manage channels, Manage roles")
    
    @commands.command(pass_context=True, name="setpassword")
    @checks.admin_or_permissions(manage_channels=True)
    async def set_password(self, ctx, channel_id):
        """Allows you to set a password for that channel"""
        channel = self.bot.get_channel(channel_id)
        
        if channel is not None:
            await self.Pswd(ctx,channel,auth=False)

        else:
            await self.bot.send_message(ctx.message.channel, "Channel not found! Make sure to use the channel ID")

    @commands.command(pass_context=True, name="removepassword")
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_password(self, ctx, channel_id):
        """Allows you to remove a password from that channel"""
        try: #if issue with perms
            channel = self.bot.get_channel(channel_id)
            
            if channel is None:
                await self.bot.send_message(ctx, "Channel not found!")
                return
            
            if isinstance(channel.type, type(discord.ChannelType.text)):
                perms = discord.PermissionOverwrite(read_messages=True)
                await self.bot.edit_channel_permissions(channel, ctx.message.server.default_role, perms)

            elif isinstance(channel.type, type(discord.ChannelType.voice)):
                perms = discord.PermissionOverwrite(connect=True)
                await self.bot.edit_channel_permissions(channel, ctx.message.server.default_role, perms)
            
            #Removes the item from the DB
            db.users.delete_one({'CHANNEL':channel_id})
            await self.bot.send_message(ctx.message.channel, "Password removed!")

        except discord.Forbidden:
            await self.bot.send_message(ctx.message.channel, "Humm... I wasn't able to do that... Check my discord permissions.")


    @commands.command(pass_context=True, name="enterpassword")
    @commands.cooldown(1, 30, commands.BucketType.user)
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
