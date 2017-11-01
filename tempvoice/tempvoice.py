import discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help

#Created by The Tasty Jaffa
#Requested by idlechatter
#Thanks to Tobotimus for helping with the listener function

def get_role(ctx, role_id):
    roles = set(ctx.message.server.roles)
    for role in roles:
        if role.id == role_id:
            return role
    return None

class TempVoice:
    def __init__(self, bot):
        self.bot = bot
        self.check_empty = dataIO.load_json("data/Tasty/TempVoice/VoiceChannel.json")
        self.settings = dataIO.load_json("data/Tasty/TempVoice/settings.json")
        
        for x in self.bot.servers:
            try:
                print("Testing Values for settings.json in /Tatsy/TempVoice")
                self.settings[x.id]
            except:

                self.settings[x.id]={
                    'role':None,
                    'channel':None,
                    'type':False,
                    }
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)

    @commands.group(name="setvoice", pass_context=True)
    @checks.admin()
    async def VoiceSet(self, ctx):

        """Changes the settings for this cog, use with no sub command to get infomation on the cog, and current setings"""

        if ctx.invoked_subcommand is None:
            info = ''.join('{}{}\n'.format(key, val) for key, val in self.settings[ctx.message.server.id].items())
            em = discord.Embed(title="Tempary voice channel settings", description="""voice [name]

Creates a Voice channel named after the user who called it or by the optional parameter [name] - must have " around the entire name (some limitations such as length apply)

channel <channel_id>
Selects a voice channel which users can join to create a tempary voice channel

role <role_name>
Sets the role which can use the commands/make temporary voice channels -- example - [p]setvoice role name autovoice

type <mode_number>
Sets the mode type for the server
Mode = 1, Use of a Channel.
Mode = 2, Use of a command.

Also make sure I have "move members" and "manage channels" permissions! """, colour=0xff0000)
            
            if self.settings[ctx.message.server.id]["type"] is True:
                rep = "Use of a Channel (mode = 1)"
            else:
                rep = "Use of a Command (mode = 2)"
                
            em.add_field(name="Type", value=rep, inline=False)
            
            try:
                em.add_field(name="channel",value = ctx.message.server.get_channel(self.settings[ctx.message.server.id]['channel']).name, inline=False)
            except:
                em.add_field(name="channel",value = "None", inline=False)
            
            em.add_field(name="Role", value = get_role(ctx, self.settings[ctx.message.server.id]['role']), inline=False)
            
            del rep
            em.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)

            em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
                    
            await self.bot.send_message(ctx.message.channel, embed=em)
            

    @VoiceSet.command(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel_id:str):

        """Enter **Voice** channel id to set the channel to join to make a new sub channel """

        
        channel = self.bot.get_channel(channel_id)#basicly just to check if it's an actual channel
        if channel is None:
            channel = discord.utils.get(ctx.message.server.channels, name=channel_id, type=discord.ChannelType.voice)
            
            if channel is None:
                await self.bot.send_message(ctx.message.channel, "That channel was not found")
                return
            
        self.settings[ctx.message.server.id]['channel']=channel.id
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)


    @VoiceSet.command(pass_context=True)
    @checks.admin()
    async def role(self, ctx, NoI:str, role:str):#NoI standing for Name or Id
        """sets the required role to use the [p]voice command"""

    
        role = discord.utils.get(ctx.message.server.roles, name=role)
        
        if role is not None:
            self.settings[ctx.message.server.id]['role'] = role.id
            dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
            
        else:
            await self.bot.send_message(ctx.message.channel, "Sorry but that role could not be found")
    
    async def AutoTempVoice(self, before, user): #Is called when Someone joins the voice channel
        """Automaticly checks the voice channel for users and makes a channel for them"""
        
        for value in set(self.settings.items()):
            if value[1]['type']==True:
                try:
                    if value[1]['channel']==user.voice_channel.id:
                        perms = discord.PermissionOverwrite(mute_members=True, deafen_members=True, manage_channels=True)#Sets permisions
                        perms = discord.ChannelPermissions(target=user, overwrite=perms)#Sets the channel permissions for the person who sent the message

                        channel = await self.bot.create_channel(self.bot.get_server(value[0]), user.name, perms, type=discord.ChannelType.voice)#creates a channel           
                        self.check_empty.append([channel.id, value[0]]) #Multidimentional list
                        dataIO.save_json("data/Tasty/VoiceChannel.json", self.check_empty)#saves the new file
                        await self.bot.move_member(user, channel)
                        
                except:
                    pass
            
                
    @VoiceSet.command(name="type", pass_context=True)
    @checks.admin()
    async def VoiceType(self, ctx, Voice:int):
        """Sets the Voice channel creation type - [2] = use of command - [1] = Use of channel"""
        
        if Voice == 2:
            self.settings[ctx.message.server.id]['type']=False

            await self.bot.send_message("Mode changed to use of a command `[p]voice` [Mode = 2]")
            
        elif Voice == 1:
            self.settings[ctx.message.server.id]['type']=True
            await self.bot.send_message("Mode changed to use of a channel `Join the set channel` [Mode = 1]")
            
        else:
            await self.bot.send_message(ctx.message.channel, "Sorry that's not a valid type")

        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)                  
    
    @commands.command(name="voice", pass_context=True)
    async def voice(self, ctx, name:str=''): #actual command
        """Creates a voice channel use opptional argument <name> to spesify the name of the channel, Use `" "` around the name of the channel"""
        #This can be updated
        if self.settings[ctx.message.server.id]['type'] == False:
            roles = set(ctx.message.author.roles)
            if self.settings[ctx.message.server.id]['role'] is not None:
                for role in roles:
                    if role.id == self.settings[ctx.message.server.id]['role']:
                        if name =='': #Tests if no name was passed
                            name = ctx.message.author.name #Sets it to the name of whoever sent the message
                        
                        try:
                            perms = discord.PermissionOverwrite(mute_members=True, deafen_members=True, manage_channels=True)#Sets permisions
                            perms = discord.ChannelPermissions(target=ctx.message.author, overwrite=perms)#Sets the channel permissions for the person who sent the message
                            channel = await self.bot.create_channel(ctx.message.server, name, perms, type=discord.ChannelType.voice)#creates a channel          

                            self.check_empty.append([channel.id, ctx.message.server.id]) #Multidimentional list
                            dataIO.save_json("data/Tasty/VoiceChannel.json", self.check_empty)#saves the new file
                            
                        except Exception as e:
                            print(e)
                            await self.bot.send_message(ctx.message.channel, "An error occured - check logs")
                            pass

                        break #Exits the for loop


            else:
                if name =='': #Tests if no name was passed
                    name = ctx.message.author.name #Sets it to the name of whoever sent the message
                
                try:
                    perms = discord.PermissionOverwrite(mute_members=True, deafen_members=True, manage_channels=True)#Sets permisions
                    perms = discord.ChannelPermissions(target=ctx.message.author, overwrite=perms)#Sets the channel permissions for the person who sent the message
                    channel = await self.bot.create_channel(ctx.message.server, name, perms, type=discord.ChannelType.voice)#creates a channel          
                    self.check_empty.append([channel.id, ctx.message.server.id]) #Multidimentional list or array
                    dataIO.save_json("data/Tasty/VoiceChannel.json", self.check_empty)#saves the new file
                    
                except Exception as e:
                    print(e)
                    await self.bot.send_message(ctx.message.channel, "An error occured - check logs")
                    pass

    async def server_join(self, server):
        self.settings[server.id]={
            'role':None,
            'channel':None,
            'type':False,
            }

    async def Check(self): #Loops around untill channel is empty ~~ also A LOT of nested stuff
        DELAY = 60 #Delay in seconds
        
        while self == self.bot.get_cog("TempVoice"): #While bot is online
            for index, channel in enumerate(self.check_empty):
                try: #This is here incase it could not find the channel
                    if self.bot.get_server(channel[1]).get_channel(channel[0]).voice_members == []: #Is the channel Empty (returns empty list if empty) - If no channel - attribute error
                        current = self.bot.get_server(channel[1]).get_channel(channel[0]) #Get's the current channel 1st index (0) is the channel id, second (1) is the server id of that channel
                        
                        try:
                            await self.bot.delete_channel(current)
                            del self.check_empty[index] #Removes it from list
                            dataIO.save_json("data/Tasty/VoiceChannel.json",self.check_empty)# saves new list
                        
                        except Exception as e:
                            print("====================")
                            print(e)
                            print("====================")
                            await self.bot.send_message(ctx.message.channel, "An error occured - check logs")

                except AttributeError: #Removes it from file if it does
                    del self.check_empty[index]
                    dataIO.save_json("data/Tasty/VoiceChannel.json",self.check_empty)
                    pass

            dataIO.save_json("data/Tasty/VoiceChannel.json",self.check_empty)# saves new list
            await asyncio.sleep(DELAY)

def check_folders(): #Creates a folder
    if not os.path.exists("data/Tasty/TempVoice"):
        print("Creating data/Tasty/TempVoice folder...")
        os.makedirs("data/Tasty/TempVoice")

def check_files(): #Creates json files in the folder
    if not dataIO.is_valid_json("data/Tasty/TempVoice/VoiceChannel.json"):
        print("Creating empty VoiceChannel.json...")
        dataIO.save_json("data/Tasty/TempVoice/VoiceChannel.json", [])

    if not dataIO.is_valid_json("data/Tasty/TempVoice/settings.json"):
        print("Creating empty settings.json...")    
        dataIO.save_json("data/Tasty/TempVoice/settings.json", {})

def setup(bot):
    logger = logging.getLogger('aiohttp.client')
    logger.setLevel(50)  # Stops warning spam
    check_folders()
    check_files()
    n = TempVoice(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.Check())
    bot.add_listener(n.AutoTempVoice, 'on_voice_state_update') #Tahnkyou to Tobotimus for giving a simple example on listeners
    bot.add_listener(n.server_join, "on_server_join")
    bot.add_cog(n)
