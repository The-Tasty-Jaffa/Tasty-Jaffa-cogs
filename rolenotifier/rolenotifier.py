from discord.ext import commands
from discord import Embed
from .utils import checks
from .utils.dataIO import dataIO
import os

#requested by Freud
#programed by The Tasty Jaffa
#Some help with gramma from Freud (and also testing it making sure it worked)

class RoleNotifier:
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/Tasty/AutoRoleDM/settings.json")
        for x in self.bot.servers:
            try:
                print("Testing Values for settings.json in /Tatsy/AutoRoleDM")
                self.settings[x.id]
            except:

                self.settings[x.id]={
                    }
        dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)
        
    async def Role_Update_check(self, before, after):

        check_roles = [r for r in after.roles if r not in before.roles]
        for role in check_roles:
            try: #Should catch index error (ie don't alert)
                msg = self.settings[after.server.id][role.name] 
                await self.bot.send_message(after, msg.format(role.name, after.server.name, after.mention, after.name))
            except:
                pass
    
    @commands.command(pass_context=True, name="AutoRoleHelpTastyCogs")
    @checks.admin_or_permissions(manage_roles=True)
    async def Notification_message_syntax(self, ctx):
        """Provides infomation on the syntax of what is sent and how to use it"""
        em = Embed(tile="Infomation on how to use the notification system")
        em.add_field(name="Use of `{0}`", Value = "The name of the role that was gained", inline=True)
        em.add_field(name="Use of `{1}`", value = "The name of the server that the role was gained in", inline=True)
        em.add_field(name="Use of `{2}`", value = "Mentions the user who gained the role", inline=True)
        em.add_field(name="Use of `{3}`", value = "The name of the user who gained the role", inline=True)
        em.add_field(name="How to enter the msg", value='Use speech marks `" "` around the msg -> example `[p]setroles Member "Well done {2}! You have gained {0}!"`', inline=True)
        em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
        await self.bot.send_message(ctx.message.channel, embed=em)
    
    @commands.command(pass_context=True, name="setroles")
    @checks.admin_or_permissions(manage_roles=True)
    async def set_roles(self, ctx, role_name:str, msg:str="Well done {2}! In {1} you have just gained {0} role"):
        """For documentation of this command check the gitpage, use speech marks for the [msg] paramater"""
        await self.bot.send_message(ctx.message.channel, "This will dm a user with `{}` when then gain the `{}` role? \n\n __are you sure you want this? **y/n**__".format(msg, role_name))
        response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)
        if response.content.lower() == 'y':
            self.settings[ctx.message.server.id][role_name] = msg
            dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)
            await self.bot.send_message(ctx.message.channel, "Saved! -- Make sure to have a look at the documention on the git repo page!")

        else:
            await self.bot.send_message(ctx.message.channel, "Aborted! -- Make sure to have a look at the documention on the git repo page!")

    @commands.command(pass_context=True, name="listroles")
    @checks.admin_or_permissions(manage_roles=True)
    async def list_roles(self, ctx):
        """Lists all the roles that have been given/set a notification for in this server."""

        em = Embed(title="All roles and their notification messages")
        for role_name, msg in self.settings[ctx.message.server.id].items():
            em.add_field(name=role_name, value=msg, inline=True)
        
        em.set_footer(text="This cog can be found here - https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/")
        await self.bot.send_message(ctx.message.channel, embed=em)

    @commands.command(name="removerole", pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove_roles(self, ctx, role_name):
        """Removes roles from notifications, use `[p]listroles` to find out what roles are set to be notifified"""
        await self.bot.send_message("This will remove the `{}` role and people who gain this role will no longer be notified. \n\n__are you sure you want this? **y/n**__".format(msg, role_name))
        response = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)
        if response.lower() == 'y':
            try:
                del self.settings[ctx.message.server.id][role_name]
                dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", self.settings)
                await self.bot.send_message(ctx.message.channel, "Saved! -- Make sure to have a look at the documention on the git repo page!")
            except:
                await self.bot.say("Woops! That role hasn't been set yet!")
        else:
            await self.bot.send_message(ctx.message.channel, "Aborted! --  Make sure to have a look at the documention on the git repo page!")

    async def server_join(self, server):
        self.settings[server.id]={
        }

def check_folders(): #Creates a folder
    if not os.path.exists("data/Tasty/AutoRoleDM"):
        print("Creating data/Tasty/AutoRoleDM folder...")
        os.makedirs("data/Tasty/AutoRoleDM")

def check_files(): #Creates json files in the folder
    if not dataIO.is_valid_json("data/Tasty/AutoRoleDM/settings.json"):
        print("Creating empty settings.json...")    
        dataIO.save_json("data/Tasty/AutoRoleDM/settings.json", {})
  
def setup(bot):
    check_folders()
    check_files()
    n = RoleNotifier(bot)
    bot.add_listener(n.Role_Update_check, 'on_member_update')
    bot.add_listener(n.server_join, "on_server_join")
    bot.add_cog(n)
