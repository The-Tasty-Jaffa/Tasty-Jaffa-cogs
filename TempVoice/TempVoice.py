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

    @commands.group(name="voiceset", pass_context=True)
    @checks.admin()
    async def VoiceSet(self, ctx):
        """Changes the settings for this cog use with no sub to get info on how to use, and current setings"""

        if ctx.invoked_subcommand is None:
            info = ''.join('{}{}\n'.format(key, val) for key, val in self.settings[ctx.message.server.id].items())
            em = discord.Embed(title="Tempary voice channel settings", description="`To change the settings please use '[p]voiceset channel <channel id/name>' to make a channel for that user - use '[p]Voiceset role <name(use if entering name) or id(use if entering role id (get by using [p]roleid))> <rolename or roleid>' to limit who can make temp voice channels - Use '[p]Voiceset mode <mode>' to change the mode <1>=Join channel - Temp channel created - user moved <2> user uses '[p]voice' to make a temp voice channel.`", colour=0xff0000)
            
            if self.settings[ctx.message.server.id] == True:
                rep = "1"
            else:
                rep = "2"
                
            em.add_field(name="Type", value=rep, inline=False)
            try:
                em.add_field(name="channel",value = ctx.message.server.get_channel(self.settings[ctx.message.server.id]['channel']).name, inline=False)
            except:
                em.add_field(name="channel",value = "None", inline=False)
            
            em.add_field(name="Role", value = get_role(ctx, self.settings[ctx.message.server.id]['role']), inline=False)
            del rep
    
            em.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
                    
            await self.bot.send_message(ctx.message.channel, embed=em)
            

    @VoiceSet.command(name="channel", pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel_in:str):
        """Enter **Voice** channel id or name Note channel names do not work if they have space in them."""
        
        channel = self.bot.get_channel(channel_in)#basicly just to check if it's an actual channel
        if channel is None:
            channel = discord.utils.get(ctx.message.server.channels, name=channel_in, type=discord.ChannelType.voice)
            
            if channel is None:
                await self.bot.send_message(ctx.message.channel, "That channel was not found")
                return
            
        self.settings[ctx.message.server.id]['channel']=channel.id
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)


    @VoiceSet.command(name="role", pass_context=True)
    @checks.admin()
    async def role(self, ctx, NoI:str, role:str):#NoI standing for Name or Id
        """sets the required role to use the [p]voice command"""
        if NoI == 'name':
            role = discord.utils.get(ctx.message.server.roles, name=role)
            
            if role is not None:
                self.settings[ctx.message.server.id]['role'] = role.id
                
            else:
                await self.bot.send_message(ctx.message.channel, "Sorry but that role could not be found")

        elif NoI=='id':
            if role is not None:
                self.settings[ctx.message.server.id]['role'] = role.id
                
        else:
            await self.bot.send_message(ctx.message.channel, "Please use either **id** or **name** like this [p]voiceset role name TempVoice")

        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
    
    async def AutoTempVoice(self, before, user): #Is called when Someone joins the voice channel
        """Automaticly checks the voice channel for users and makes a channel for them"""
        
        for value in list(self.settings.items()):
            if value[1]['type']==True:
                if value[1]['channel']==user.voice_channel.id:
                    try:
                        perms = discord.PermissionOverwrite(mute_members=True, deafen_members=True, manage_channels=True)#Sets permisions
                        perms = discord.ChannelPermissions(target=user, overwrite=perms)#Sets the channel permissions for the person who sent the message
                        channel = await self.bot.create_channel(self.bot.get_server(value[0]), user.name, perms, type=discord.ChannelType.voice)#creates a channel          
                        self.check_empty.append([channel.id, value[0]]) #Multidimentional list or array
                        dataIO.save_json("data/Tasty/VoiceChannel.json", self.check_empty)#saves the new file
                        await self.bot.move_member(user, channel)
                        
                    except Exception as e:
                        print(e)
                        pass
            
                
    @VoiceSet.command(name="type", pass_context=True)
    @checks.admin()
    async def VoiceType(self, ctx, Voice:int):
        """Sets the Voice channel creation type - [1] = use of command - [2] = Use of channel"""
        
        if Voice == 2:
            self.settings[ctx.message.server.id]['type']=False
            
        elif Voice == 1:
            self.settings[ctx.message.server.id]['type']=True
            
        else:
            await self.bot.send_message(ctx.message.channel, "Sorry that's not a valid type")

        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)                  
    
    @commands.command(name="voice", pass_context=True)
    async def voice(self, ctx, name:str=''): #actual command
        """Creates a voice channel use opptional argument <name> to spesify the name of the channel"""
        if self.settings[ctx.message.server.id]['type'] == False:
            print()
            print(ctx.message.author.roles)
            print()
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
                            self.check_empty.append([channel.id, ctx.message.server.id]) #Multidimentional list or array
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

    async def Check(self): #Loops around untill channel is empty ~~ also A LOT of nested stuff
        DELAY = 60 #Delay in seconds
        
        while self == self.bot.get_cog("TempVoice"): #While bot is online
            for index, channel in enumerate(self.check_empty):
                try: #This is here incase it could not find the channel
                    if self.bot.get_server(channel[1]).get_channel(channel[0]).voice_members == []: #Is the channel Empty (returns empty list if empty) - If no channel - attribute error
                        current = self.bot.get_server(channel[1]).get_channel(channel[0]) #Get's the current channel 1st index (0) is the channel id, second (1) is the server id of that channel
                        
                        try:
                            print("deleting", current.name)
                            await self.bot.delete_channel(current)
                            del self.check_empty[index] #Removes it from list
                            dataIO.save_json("data/Tasty/VoiceChannel.json",self.check_empty)# saves new list
                        
                        except Exception as e:
                            print("====================")
                            print(e)
                            print("====================")
                            await self.bot.send_message(ctx.message.channel, "An error occured - check logs")

                except AttributeError: #Removes it from file if it does
                    print("Removing Unfound channel")
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
    bot.add_cog(n)
