from discord.ext import commands

#requested by Freud
#programed by The Tasty Jaffa

#V 0.1
#Simple core structure.

class Role_Updated:
    def __init__(self, bot):
        self.bot = bot
    async def Role_Update_check(self, before, after):

        check_roles = [r for r in after.roles if r not in before.roles] #This will add all roles that where not there before
        
        for role in check_roles:
            print(role.name)
            print(role)
            if role.name == "Member": #Checks if it is equal to a role called "Member" - This will be modifiable later
                msg = "Hello {after.mention}, \n\nThanks for sticking around with RuneLinked! As you have now been with us for 24 hours you have now been granted the Member role! This role gives you permissions to change your nickname, attach images as well as an awesome purple colour! \n\nWhy not check out some of the awesome things in our discord such as our **Treasure Hunt**! This can be started by using the `!hunt` command in any channel. Also check out RuneInfo, a great runescape bot for all your needs. \n\nIf you have any questions feel free to ask one of the members of staff and we will be glad to help.\n\nThanks \n\n**The RuneLinked Team**".format(after=after)
                await self.bot.send_message(after, msg)

def setup(bot):
    n = Role_Updated(bot)
    bot.add_listener(n.Role_Update_check, 'on_member_update') #Adds a listener -- This will call the "Roke_Update_check" def when a members status updates ("on_member_update")
    bot.add_cog(n)
