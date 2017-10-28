import discord, os, logging
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from .utils.chat_formatting import pagify, box

#The Tasty Jaffa
#Requested by Freud

class say:
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/Tasty/say/settings.json")

        print("Testing values in data/Tasty/say")
        for server in self.bot.servers:
            try:
                self.settings[server.id]["MAX_MENTIONS"]
                self.settings[server.id]["ROLE"]
                self.settings[server.id]["USERS"]
            except:
                self.settings[server.id] = {}
                self.settings[server.id]["MAX_MENTIONS"]=3
                self.settings[server.id]["ROLE"] = None
                self.settings[server.id]["USERS"] = []
        
    @commands.group(name="setsay", pass_context=True, no_pm=True, invoke_without_command=True)
    async def sayset(self, ctx):
        """The 'Say' command set

add - Adds a user to have the abillity to use the say command
list - list users allowed and permited role
remove - Removes a user to have the abillity to use the say command"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(ctx.message.channel, "```Please use the say command with: \n add - Adds a **user** to have the abillity to use the say command \n remove - Removes a **user** to have the abillity to use the say command \n role - Adds a role and those with it can use the speak command \n list - lists permited users and the permited role```")

    @sayset.command(name="list", pass_context=True)
    @checks.admin_or_permissions()
    async def say_list(self,ctx):
        names = []
        for user_id in self.settings[ctx.message.server.id]["USERS"]:
            names.append(discord.utils.get(self.bot.get_all_members(), id=user_id).name)
                    
        msg = ("+ Permited\n"
               "{}\n\n"
               "".format(", ".join(sorted(names))))

        for page in pagify(msg, [" "], shorten_by=16):
            await self.bot.say(box(page.lstrip(" "), lang="diff"))

        await self.bot.send_message(ctx.message.channel, "Permited Role: **{}**".format(self.settings[ctx.message.server.id]["ROLE"]))
        
    @sayset.command(name="add", pass_context=True, no_pm=True)
    @checks.admin_or_permissions()
    async def say_add (self, ctx, user: discord.Member):
        """Adds a [user] to have the abillity to use the say command"""
        self.settings[ctx.message.server.id]["USERS"].append(user.id)
        self.save()
        await self.bot.send_message(ctx.message.channel, "Done!")

    @sayset.command(name="remove", pass_context=True, no_pm=True)
    @checks.admin_or_permissions()
    async def say_remove (self, ctx, user: discord.Member):
        """Removes a [user] to have the abillity to use the say command"""
        try:
            self.settings[ctx.message.server.id]["USERS"].remove(user.id)
            self.save()
            await self.bot.send_message(ctx.message.channel, "Done!")

        except:
            await self.bot.send_message(ctx.message.channel, "Are you sure that {} had the permision in the first place?".format(user.mention))

    @sayset.command(name="role", pass_context=True)
    @checks.admin_or_permissions()
    async def say_role(self, ctx, role_name:str):
        self.settings[ctx.message.server.id]["ROLE"]=role_name
        self.save()
        await self.bot.send_message(ctx.message.channel, "Role {} added".format(role_name))
            

    @commands.command(name="speak", pass_context=True)
    async def bot_say(self, ctx, *, text):
        """The bot says what you tell it to"""

        if '@everyone' in ctx.message.content and '@here' in ctx.message.content and len(ctx.message.mentions) > self.settings[ctx.message.server.id]["MAX_MENTIONS"]:
            await self.bot.send_message(ctx.message.channel, "Woh! {}, please don't do that".format(ctx.message.author.mention))
            return
    
        #IF there are no mentions such as @everyone or @here must test useing a string
        
        if ctx.message.channel.permissions_for(ctx.message.server.me).manage_messages:         
            if ctx.message.author.id in self.settings[ctx.message.server.id]["USERS"] or self.settings[ctx.message.server.id]["ROLE"] in ctx.message.author.roles.names:
                await self.bot.delete_message(ctx.message)
                await self.bot.send_message(ctx.message.channel, text)
            else: 
                await self.bot.say("You need to be given access to this command") 
        else: 
            await self.bot.say("This command requires the **Manage Messages** permission.")

    async def save(self):
        dataIO.save_json("data/Tasty/say/settings.json", self.settings)

    async def server_join(self, server):
        self.settings[server.id]={
            "MAX_MENTIONS":3,
            "ROLE":None,
            "USERS":[],
        }

        self.save()
        
def check_folders(): #Creates a folder
    if not os.path.exists("data/Tasty/say"):
        print("Creating data/Tasty/say folder...")
        os.makedirs("data/Tasty/say")

def check_files(): #Creates json files in the folder
    if not dataIO.is_valid_json("data/Tasty/say/settings.json"):
        print("Creating empty settings.json...")    
        dataIO.save_json("data/Tasty/say/settings.json", {})

def setup(bot):
    check_folders()
    check_files()

    n = say(bot)
    bot.add_listener(n.server_join, "on_server_join")
    bot.add_cog(n)

