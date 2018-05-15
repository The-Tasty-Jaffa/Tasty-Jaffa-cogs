from discord.ext import commands
from discord import Embed
from discord import Forbidden
from .utils import checks
from .utils.dataIO import dataIO
import os

#requested by Freud
#Improved thanks to the community!
#programed by The Tasty Jaffa
#Some help with gramma from Freud (and also testing it making sure it worked)


class RoleNotifier:
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/Tasty/AutoRoleDM/settings.json")
        # Checks the data in the file (ie updating or bot joined server when offline)
        for x in self.bot.servers:
            try:
                #to avoid breaking things, checks if it is in correct format
                items = self.settings[x.id]

                for key,value in items.items():
                    if type(value) == type(dict()):
                        continue

                    self.settings[x.id][key] = {'MSG':value, 'CHANNEL':None}                   

            except Exception as e:
                self.settings[x.id]={
                    }

        dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)

    #Data validity checker (if joined server when bot was down)
    async def data_check(self): #When servers are aviable
        for x in self.bot.servers:
            try:
                #to avoid breaking things, checks if it is in correct format
                items = self.settings[x.id]

                for key,value in items.items():
                    if type(value) == type(dict()):
                        continue

                    self.settings[x.id][key] = {'MSG':value, 'CHANNEL':None}                   

            except Exception as e:
                self.settings[x.id]={
                    }

        dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)

    #Checks if it needs to send a notification
    async def Role_Update_check(self, before, after):

        check_roles = [r for r in after.roles if r not in before.roles]
        for role in check_roles:
            if role.name in self.settings[after.server.id]:

                #Sets the notification destination (channel or user)
                if self.settings[after.server.id][role.name]['CHANNEL'] is not None:
                    channel = self.settings[after.server.id][role.name]['CHANNEL']
                    channel = self.bot.get_channel(channel)
                else:
                    channel = after

                try:
                    msg = self.settings[after.server.id][role.name]['MSG']
                    await self.bot.send_message(channel, msg.format(role.name, after.server.name, after.mention, after.name))
                
                except Forbidden:
                    await self.bot.send_message(after.server.owner, "I could not send a message to {0}. \n I either cannot send messsage to the channel or the user does not accept Direct messages.".format(channel.name))

    #General spesific help with the cog
    @commands.group(pass_context=True, name="setroles")
    @checks.admin_or_permissions(manage_roles=True)
    async def set_notification_roles(self, ctx): 
        """Command group: Use with no sub command for infomation on the syntax on how to use this cog"""
        
        if ctx.invoked_subcommand is None:
            em = Embed(tile="Infomation on how to use the notification system, use `[p]help setnotifiroles` to find right sub commands comands")
            em.add_field(name="Use of `{0}`", value = "The name of the role that was gained", inline=False)
            em.add_field(name="Use of `{1}`", value = "The name of the server that the role was gained in", inline=False)
            em.add_field(name="Use of `{2}`", value = "Mentions the user who gained the role", inline=False)
            em.add_field(name="Use of `{3}`", value = "The name of the user who gained the role", inline=False)
            em.add_field(name="How to enter the msg", value='example `[p]setroles add Member Well done {2}! You have gained {0}!`', inline=False)
            em.add_field(name="Subcommands", value='Use `[p]help setroles` to find out all the subcommands and what they do!', inline=False)
            em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
            await self.bot.send_message(ctx.message.channel, embed=em)
    
    @set_notification_roles.command(pass_context=True, name="add")
    @checks.admin_or_permissions(manage_roles=True)
    async def set_roles(self, ctx, role_name:str, *, msg:str="Well done {2}! In {1} you have just gained {0} role"):
        """Adds an alert for a role - For infomation on this command use `[p]setroles`"""

        #Default settings
        channel = None

        if len(msg) > 1500:
            await self.bot.send_message(ctx.message.channel, "Sorry the message is too long to continue with the process!")
            return

        await self.bot.send_message(ctx.message.channel, "Is this to be sent though a __**Direct message**__? **y/n**")
        response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)

        #If it is to be Direct message
        if 'y' in response.content.lower(): 
            await self.bot.send_message(ctx.message.channel, "This will dm a user with `{}` when they gain the `{}` role? \n\n __are you sure you want this? **y/n**__".format(msg, role_name))
            response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)
        
        #Get the channel if to be sent to a channel
        else:
            await self.bot.send_message(ctx.message.channel, "Please enter the **channelID** for which the notification should be sent?")
            channel = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)
            channel = self.bot.get_channel(channel.content)
            
            if channel is None:
                await self.bot.send_message(ctx.message.channel, "No channel with this id was found, Aborting!!")
                return
            
            await self.bot.send_message(ctx.message.channel, "This will send a message in the `{}` channel with `{}` when someone gains the `{}` role? \n\n __are you sure you want this? **y/n**__".format(channel.name, msg, role_name))
            response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)
            channel = channel.id

        #Save notifcation
        if 'y' in response.content.lower() :
            self.settings[ctx.message.server.id][role_name] = {'MSG':msg, 'CHANNEL':channel}
            dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)
            await self.bot.send_message(ctx.message.channel, "Saved! -- Make sure to have a look at the documention on the git repo page!")

        else:
            await self.bot.send_message(ctx.message.channel, "Aborted! -- Make sure to have a look at the documention on the git repo page!")

    @set_notification_roles.command(pass_context=True, name="list")
    @checks.admin_or_permissions(manage_roles=True)
    async def list_roles(self, ctx):
        """Lists all the roles that have been given/set a notification for in this server."""

        em = Embed(title="All roles and their notification messages")
        for role_name, values in self.settings[ctx.message.server.id].items():
            if values['CHANNEL'] is None:
                em.add_field(name=role_name, value=values['MSG'], inline=True)

            else:
                em.add_field(name=role_name, value = values['MSG'] + "\n Channel: " + self.bot.get_channel(values['CHANNEL']).name, inline = True)

        em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
        await self.bot.send_message(ctx.message.channel, embed=em)

    @set_notification_roles.command(name="remove", pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove_roles(self, ctx, role_name):
        """Removes roles from notifications, use `[p]listroles` to find out what roles are set to be notifified"""
        await self.bot.send_message(ctx.message.channel, "This will remove the `{}` role and people who gain this role will no longer be notified. \n\n__are you sure you want this? **y/n**__".format(role_name))
        response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author, timeout=60)
        
        if response is not None and 'y' in response.content.lower():
            try:
                self.settings[ctx.message.server.id].pop(role_name)
                dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)
                await self.bot.send_message(ctx.message.channel, "Saved! -- Make sure to have a look at the documention on the git repo page!")
            except:
                await self.bot.say("Woops! That role hasn't been set yet!")
        else:
            await self.bot.send_message(ctx.message.channel, "Aborted! --  Make sure to have a look at the documention on the git repo page!")

    async def server_join(self, server):
        self.settings[server.id]={
        }

    async def server_leave(self,server):
        self.settings.remove(server.id)

def check_folders(): #Creates a folder, if it doesn't exist
    if not os.path.exists("data/Tasty/AutoRoleDM"):
        print("Creating data/Tasty/AutoRoleDM folder...")
        os.makedirs("data/Tasty/AutoRoleDM")

def check_files(): #Creates json files in the folder, if it doesn't exist
    if not dataIO.is_valid_json("data/Tasty/AutoRoleDM/settings.json"):
        print("Creating empty settings.json...")    
        dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", {})
  
def setup(bot):
    check_folders()
    check_files()

    this_cog = RoleNotifier(bot)
    
    #Data checking (ie cog was loaded or reloaded)

    #Listeners
    bot.add_listener(this_cog.Role_Update_check, 'on_member_update')
    bot.add_listener(this_cog.server_join, "on_server_join")
    bot.add_listener(this_cog.server_leave, "on_server_remove")
    bot.add_listener(this_cog.data_check, "on_ready")

    bot.add_cog(this_cog)

