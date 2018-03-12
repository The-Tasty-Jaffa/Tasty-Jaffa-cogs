import discord, logging, os, asyncio, datetime
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
        
        print("Testing Values for settings.json in /Tatsy/TempVoice")
        for x in self.bot.servers:
            try:
                self.settings[x.id]
            except:

                self.settings[x.id]={
                    'role':None,
                    'channel':None,
                    'type':False,
                    'defualt_name':"{user.nick}"
                    }
            
            #Avoid breaking things when people update
            if 'defualt_name' not in self.settings[x.id]:
                self.settings[x.id]['defualt_name']="{user.nick}"
            
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
    
    #Cog settings
    @commands.group(name="setvoice", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def VoiceSet(self, ctx):
        """Changes the settings for this cog, use with no sub command to get infomation on the cog, and current setings"""

        if ctx.invoked_subcommand is None:
            info = ''.join('{}{}\n'.format(key, val) for key, val in self.settings[ctx.message.server.id].items())
            em = discord.Embed(title="Tempary voice channel settings", description="""voice [name]
Creates a Voice channel named after the user who called it or by the optional parameter [name]

channel <channel_id>
Selects a voice channel which users can join to create a tempary voice channel (Applys to mode = 1 only)

category <category_id>
Sets the category channels should be created under (Applys to mode = 2 only)

role <role_name>
Sets the role which can use the command to make a temporary voice channel -- example - [p]setvoice role autovoice

type <mode_number>
Sets the mode type for the server
Mode = 1, Use of a Channel. `[p]setvoice type 1`
Mode = 2, Use of a command. `[p]setvoice type 2`

name <defualt_channel_name>
Sets the defualt channel name format to be used when greating a channel
Use {user.name} for the users name
Use {user.game} for the users current game they are playing
Use {user.nick} for the users Nickname in the server

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
            
            try:
                em.add_field(name="category",value = ctx.message.server.get_channel(self.settings[ctx.message.server.id]['category']).name, inline=False)
            except:
                em.add_field(name="category",value = "None", inline=False)

            em.add_field(name="Role", value = get_role(ctx, self.settings[ctx.message.server.id]['role']), inline=False)
            
            em.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
            em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
                    
            await self.bot.send_message(ctx.message.channel, embed=em)

    @VoiceSet.command(name="category", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def voice_set_category(self, ctx, category_id:str):
        """Enter **Category** id - Sets the category that channels will be created under (enter None to remove)"""
        if not category_id.isdigit():

            await self.bot.send_message(ctx.message.channel, "Category removed!")

            self.settings[ctx.message.server.id]['category'] = None
            dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
            return

        category = self.bot.get_channel(category_id)

        #If it couldn't get the channel
        if category is None:
            await self.bot.send_message(ctx.message.channel, "Woops! That its not a valid ID (or there was an issue with finding the channel)! Please make sure that you use the command with the id of a category.")
            return

        #Check that this is a category
        if category.type != 4:
            await self.bot.send_message(ctx.message.channel, "Woops! That its not a category! Please make sure that you use the command with the id of a category.")
            return
        
        await self.bot.send_message(ctx.message.channel, "Category set as {0}! New channels will be created here if a command is used".format(category.name))

        self.settings[ctx.message.server.id]['category'] = category_id
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)

    @VoiceSet.command(name="channel", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def voice_set_channel(self, ctx, channel_id:str):
        """Enter **Voice** channel id to set the channel to join to make a new sub channel """
        
        channel = self.bot.get_channel(channel_id)

        #Does this channel exist?
        if channel is None:
            channel = discord.utils.get(ctx.message.server.channels, name=channel_id, type=discord.ChannelType.voice)
            #Makes sure it can find the channel
            if channel is None:
                await self.bot.send_message(ctx.message.channel, "That channel was not found.")
                return

        if channel.type is not discord.ChannelType.voice: #Check if voice channel
            await self.bot.send_message(ctx.message.channel, "That is not a voice channel.")
            return

        await self.bot.send_message(ctx.message.channel, "Channel set!")    
        self.settings[ctx.message.server.id]['channel']=channel.id
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)

    @VoiceSet.command(name="role", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def voice_set_role(self, ctx, role_name:str=""):
        """sets the required role to use the [p]voice command (leave blank for no role)"""
    
        role = discord.utils.get(ctx.message.server.roles, name=role_name)

        if role_name == "":
            await self.bot.send_message(ctx.message.channel, "The requirement of having a role has been removed!")
            self.settings[ctx.message.server.id]['role'] = None
            dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
            return

        if role is None:
            await self.bot.send_message(ctx.message.channel, "Sorry but that role could not be found")
            return
        
        await self.bot.send_message(ctx.message.channel, "Role set!")
        self.settings[ctx.message.server.id]['role'] = role.id
        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)
            
    @VoiceSet.command(name="type", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def voice_set_type(self, ctx, voice_mode:int):
        """Sets the Voice channel creation type - [2] = use of command - [1] = Use of channel"""
        
        if voice_mode == 2:
            self.settings[ctx.message.server.id]['type']=False

            await self.bot.say("Mode changed to use of a command `[p]voice` [Mode = 2]")
            
        elif voice_mode == 1:
            self.settings[ctx.message.server.id]['type']=True
            await self.bot.say("Mode changed to use of a channel `Join the set channel` [Mode = 1]")
            
        else:
            await self.bot.send_message(ctx.message.channel, "Sorry that's not a valid type")

        dataIO.save_json("data/Tasty/TempVoice/settings.json", self.settings)                  
    
    @VoiceSet.command(name="name", pass_context=True)
    @checks.serverowner_or_permissions(manage_channels=True)
    async def voice_set_default(self,ctx,*,defualt_name:str="{user.nick}"):
        """sets the default channel name, resets with no parameters
        Allows for {user.name} for their name
        {user.game} for their currently playing status
        Many other values of user can be used as well"""
        self.settings[ctx.message.server.id]['defualt_name'] = defualt_name
        await self.say("Default channel name set to `{0}`!".format(defualt_name))
    
    #Voice command
    @commands.command(pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def voice(self, ctx, *, name:str=''): #actual command
        """Creates a voice channel use opptional argument <name> to spesify the name of the channel, Use `" "` around the name of the channel"""

        #Checks the mode (type = True (therefore mode = [1])
        if self.settings[ctx.message.server.id]['type'] != False:
            return

        if name =='': #Tests if no name was passed
            name = self.settings[ctx.message.server.id]['defualt_name'].format(user=ctx.message.author) #Sets it to the defualt name for the server

        server_role = self.settings[ctx.message.server.id]['role']
        if server_role is not None:
            for role in set(ctx.message.author.roles):
                if role.id == server_role:
                    break # If role is found
                    
            else: #If we didn't break out of the loop then the user does not have the right role      
                await self.bot.say("Sorry but you are not permited to use that command! A role is needed.")
                return # If role is found breaks loop - else statement isn't executed.

        
        #If all the requirements are met
        try:
            perms = discord.PermissionOverwrite(manage_channels=True)#Sets permisions
            perms = discord.ChannelPermissions(target=ctx.message.author, overwrite=perms)#Sets the channel permissions for the person who sent the message
            channel = await self.bot.create_channel(ctx.message.server, name, perms, type=discord.ChannelType.voice)#creates a channel          
            
            #If a category has been set 
            if self.settings[channel.server.id]['category'] is not none:
                await self.move_channel_to_category(channel.id, self.settings[channel.server.id]['category'])
                
            self.check_empty.append(channel.id) #Multidimentional list
            dataIO.save_json("data/Tasty/TempVoice/VoiceChannel.json", self.check_empty)#saves the new file
            return

        except discord.Forbidden:
            await self.bot.send_message(ctx.message.channel, "I don't have the right perrmissions for that! (I need to be able to manage channels)")
            
        except Exception as e: # if something else happens such as it's not connected or a file has been messed with and so doesn't show an error in discord channel
            print("=================")
            print(e)
            print("=================")

            await self.bot.send_message(ctx.message.channel, "An error occured - check logs")
    
    #Category implimentaion
    async def channel_to_category(self, channel_in_category_id, channel_to_move_id):
        channel_in_category = await self.bot.http.request(
            discord.http.Route(
                'GET', '/channels/{}'.format(channel_in_category_id)
            )
        ) #Gets The "channel_in_category" Categories ID

        await self.move_channel_to_category(channel_to_move_id, channel_in_category["parent_id"])

    async def move_channel_to_category(self, channel_to_move_id, category_id):

        channel = await self.bot.http.request(
            discord.http.Route(
                'GET', '/channels/{}'.format(channel_to_move_id)
            )
        ) #gets the channel we want to move data (as json) -- Could be improved further

        channel["parent_id"] = category_id #Updates with the category info that we want

        await self.bot.http.request(
            discord.http.Route(
                'PATCH', '/channels/{}'.format(channel_to_move_id)
            ), json = channel #uses PATCH method to update the channel
        )
    
    #Lister defs
    async def server_join(self, server):
        self.settings[server.id]={
            'role':None,
            'channel':None,
            'type':False,
            'defualt_name':"{user.nick}"
            }

    async def AutoTempVoice(self, before, user): #Is called when Someone joins the voice channel - Listener
        """Automaticly checks the voice channel for users and makes a channel for them"""
        
        # I cannot have any returns here so channels will be created
        if before.voice_channel is not None:
            # Did they come from a channel? 

            if before.voice_channel.id in self.check_empty:
                #Was the channel they where in a tempary channel?

                if len(before.voice_channel.voice_members) == 0: 
                    # How many people are in the channel?
                    # if zero => empty. Therefore, remove the channel
                    await self.bot.delete_channel(self.bot.get_channel(before.voice_channel.id))
                    self.check_empty.remove(before.voice_channel.id)

        if user.voice_channel is None: # Are they in a channel right now?
            return
        
        if self.settings[user.voice_channel.server.id]['type']!=True:
            return

        try:
            if self.settings[user.voice_channel.server.id]['channel']!=user.voice_channel.id:
                return
            
            position = user.voice_channel.position
            perms = discord.PermissionOverwrite(manage_channels=True)#Sets permisions
            perms = discord.ChannelPermissions(target=user, overwrite=perms)#Sets the channel permissions for the person who sent the message

            channel = await self.bot.create_channel(user.voice_channel.server, self.settings[ctx.message.server]['defualt_name'].format(user=ctx.message.author, ctx=ctx), perms, type=discord.ChannelType.voice)#creates a channel           
            
            self.check_empty.append(channel.id) #Multidimentional list
            dataIO.save_json("data/Tasty/TempVoice/VoiceChannel.json", self.check_empty)#saves the new file

            await self.channel_to_category(user.voice_channel.id, channel.id) #puts channel into the right category                
            await self.bot.move_member(user, channel)
            await self.bot.move_channel(channel, position+1)
            
        except discord.Forbidden:
            await self.bot.send_message(user.server.owner, "I need the proper permissions! I was unable to create a new channel. (Move members, Manage channels)")

    async def voice_check(self): #Loops around until channel is empty
        DELAY = 60 #Delay in seconds
        
        while self == self.bot.get_cog("TempVoice"): #While bot is online/cog is loaded

            Channels_to_remove = [] # To not looping over a list that you are modifiying
            for channel_id in self.check_empty:

                if self.bot.is_logged_in is not True: # So it doesn't go "Oh this channel doesn't exist" (becuase the bot isn't online/logged on)
                    continue
                
                current = self.bot.get_channel(channel_id)

                if current is None: # if channel doesn't exist
                    Channels_to_remove.append(channel_id)
                    continue

                if len(current.voice_members) != 0: #Is the channel Empty (returns empty list if empty) - If no channel - attribute error
                    continue

                if datetime.datetime.today() - datetime.timedelta(seconds=30) < current.created_at:
                    continue
                
                await self.bot.delete_channel(current)
                Channels_to_remove.append(channel_id) #Adds it to a list for removall
                
                await asyncio.sleep(0.5)

            for channel_id in Channels_to_remove:
                self.check_empty.remove(channel_id)

            dataIO.save_json("data/Tasty/TempVoice/VoiceChannel.json",self.check_empty)# saves new list
            await asyncio.sleep(DELAY)

        await self.bot.send_message(discord.Appinfo.owner, "Channels will no longer be deleted! An issue has ocurred. some INFO: `self.check_empty: {0} | self.bot.get_cog: {1}`".format(self.check_empty, self.bot.get_cog("TempVoice")))
        #Some instances have issues here (not sure why still)

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
    check_folders()
    check_files()

    n = TempVoice(bot)

    loop = asyncio.get_event_loop()
    loop.create_task(n.voice_check())

    bot.add_listener(n.AutoTempVoice, 'on_voice_state_update') #Thankyou to Tobotimus for giving a simple example on listeners
    bot.add_listener(n.server_join, "on_server_join")

    bot.add_cog(n)
