import discord, logging, os, asyncio
from discord.ext import commands
from .utils.dataIO import dataIO

#Created by The Tasty Jaffa
#Idea by idlechatter

class TempVoice:
    def __init__(self, bot):
        self.bot = bot
        self.check_empty = dataIO.load_json("data/Tasty/VoiceChannel.json")
        
    @commands.command(name="voice", pass_context=True)
    async def voice(self, ctx, name:str=''): #actual command
        """Creates a voice channel use opptional argument <name> to spesify the name of the channel"""
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
    if not os.path.exists("data/Tasty"):
        print("Creating data/Tasty folder...")
        os.makedirs("data/Tasty")

def check_files(): #Creates json files in the folder
    if not dataIO.is_valid_json("data/Tasty/VoiceChannel.json"):
        print("Creating empty VoiceChannel.json...")
        dataIO.save_json("data/Tasty/VoiceChannel.json", [])

def setup(bot):
    logger = logging.getLogger('aiohttp.client')
    logger.setLevel(50)  # Stops warning spam
    check_folders()
    check_files()
    n = TempVoice(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.Check())
    bot.add_cog(n)

