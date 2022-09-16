from discord import Embed
from discord import Forbidden
from redbot.core import Config, checks, commands


# requested by Freud
# Improved thanks to the community!
# programed by The Tasty Jaffa
# 2017 - 2018
# Some help with gramma from Freud (and also testing it making sure it worked)

class RoleNotifier(commands.Cog):
    __author__ = "The Tasty Jaffa"
    __version__ = "2.2.6"

    def __init__(self, bot):
        self.bot = bot
        self.Alerts = Config.get_conf(self, identifier=1, force_registration=True)
        default_value = {
            'alerts': {},
        }
        # Each server has dict with "alerts"
        # "alerts" is a dict of lists ie: role_name: [], some_other_role_name: [] ..etc
        self.Alerts.register_guild(**default_value)

    # Checks if it needs to send a notification
    async def role_update_check(self, before, after):
        """Checks added roles and sends alerts as needed"""

        async with self.Alerts.guild(after.guild).alerts() as alerts:
            check_roles = set(after.roles) - set(before.roles)
            for role in check_roles:
                if role.name in alerts:
                    break  # A role was found
            else:
                return  # No role with that was found

            # Alerts is a dict of lists ie: role_name: [], some_other_role_name: [] ..etc
            # Sets the notification destination (channel or user)
            for alert in alerts[role.name]:
                if alert['channel'] is not None:
                    channel = after.guild.get_channel(int(alert['channel']))
                    if channel is None:
                        await after.guild.owner.send(
                            "A alert is set to use a channel that doesn't exist! (no channel exists with ID `{0}`".format(
                                alert['channel']))
                        continue

                else:
                    channel = after  # The channel we want is a users Direct Message channel

                try:
                    text = alert['text']

                    if alert['em']:
                        embed = Embed(title="You gained a new role!",
                                      description=text.format(role=role, server=after.guild, user=after))
                        # embed.set_thumbnail(after.avatar_url)
                        await channel.send(embed=embed)
                        continue

                    else:
                        await channel.send(text.format(role=role, server=after.guild, user=after))
                        continue

                except Forbidden:
                    print("Forbidden from sending a role alert message - notifiying server owner.")
                    await after.server.owner.send_message(after.server.owner,
                                                          "I could not send a message to {0}. \n I either cannot send messsage to the channel or the user does not accept Direct messages.".format(
                                                              channel.name))
                    pass

    # General spesific help with the cog
    @commands.group(name="rolealert", aliases=["setroles"])
    @checks.admin_or_permissions(manage_roles=True)
    async def set_notification_roles(self, ctx):
        """Command group: Use with no sub command for infomation on the syntax on how to use this cog"""

        if ctx.invoked_subcommand is None:
            em = Embed(
                tile="Infomation on how to use the notification system, use `[p]help rolealert` to find right sub commands comands")
            em.add_field(name="Use of `{role.name}`", value="The name of the role that was gained", inline=False)
            em.add_field(name="Use of `{server.name}`", value="The name of the server that the role was gained in",
                         inline=False)
            em.add_field(name="Use of `{user.mention}`", value="Mentions the user who gained the role", inline=False)
            em.add_field(name="Use of `{user.display_name}`",
                         value="The name of the user who gained the role (Warning! if someone has @everyone in there name it could ping everyone!)",
                         inline=False)
            em.add_field(name="How to enter the msg",
                         value='example: `[p]setroles add "Member" Well done {user.mention}! You have gained {role.name}!`',
                         inline=False)
            em.set_footer(text="This cog can be found here - https://gitlab.com/The_Tasty_Jaffa/Tasty-Jaffa-cogs/")
            await ctx.channel.send(embed=em)

    @set_notification_roles.command(name="add", no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def set_roles(self, ctx, role_name: str, *,
                        msg: str = "Well done {user.display_name}! In {server.name} you have just gained {role.name} role"):
        """Adds an alert for a role - For infomation on this command use `[p]setroles`"""

        # After each question that part of the message changed
        # which is then used to construct a confirmation sentence

        # Default settings
        channel = None

        if len(msg) > 1000:
            await ctx.send("Sorry the message is too long to continue with the process!")
            return

        def check_author(msg):
            return msg.author == ctx.author

        # Should it be sent as an Embed?
        await ctx.send("Is this to be sent as a __**Embed**__? **y/n**")
        response = await self.bot.wait_for("message", check=check_author, timeout=120)
        if response is not None and 'y' in response.content.lower():
            em = True
            em_con = "embed"

        else:
            em = False
            em_con = "message"

        await ctx.send("Is this to be sent though a __**Direct message**__? **y/n**")
        response = await self.bot.wait_for("message", check=check_author, timeout=120)

        # If it is to be Direct message
        if response is not None and 'y' in response.content.lower():
            channel_con = "dm a user with a `{0}`".format(em_con)
            # Channel_con to generate alert confirmation text

        # Get the channel if to be sent to a channel
        else:
            await ctx.send("Please enter the **channelID** for which the notification should be sent?")
            channel = await self.bot.wait_for("message", check=check_author, timeout=120)

            if channel.content.isdigit():
                channel = ctx.guild.get_channel(int(channel.content))

            else:
                await ctx.send("That wasn't a vaid ID. Aborting!!")
                return

            if channel is None:
                await ctx.send("No channel with this id was found, Aborting!!")
                return

            channel_con = "send a `{1}` in the `{0}` channel with".format(channel.name, em_con)
            channel = channel.id  # Set as channel id when saving

        await ctx.send(
            "This will {channel} the message '{msg}' when someone gains the `{role}` role? \n\n __are you sure you want this? **y/n**__".format(
                channel=channel_con, msg=msg, role=role_name))
        response = await self.bot.wait_for("message", check=check_author, timeout=120)

        # Save notifcation
        if response is not None and 'y' in response.content.lower():
            async with self.Alerts.guild(ctx.guild).alerts() as alert_dict:
                if role_name not in alert_dict:
                    alert_dict[role_name] = []
                alert_dict[role_name].append({'text': msg, 'channel': channel, 'em': em})
                await ctx.send("Saved! -- Make sure to have a look at the documention on the git repo page!")

        else:
            await ctx.send("Aborted! -- Make sure to have a look at the documention on the git repo page!")

    @set_notification_roles.command(name="list", no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def list_roles(self, ctx, role_name=None):
        """Lists all the roles that have been given/set a notification for in this server."""
        msg = ""
        append_to_msg = "- All notification messages\n"

        async with self.Alerts.guild(ctx.guild).alerts() as alert_dict:

            if role_name is not None and role_name in alert_dict:  # Check if it is only showing it for one role (Role has been set when using a command)
                for num, alert in enumerate(alert_dict[role_name]):
                    # Beging alert msg
                    append_to_msg += "+ " + str(num) + ":\nAlert text: " + alert['text']

                    if alert['channel'] is None:
                        append_to_msg += "\nChannel = DM"

                    else:
                        append_to_msg += "\nChannel = {}".format(ctx.guild.get_channel(alert['channel']).name)

                    if alert['em']:
                        append_to_msg += "\nSent in an embed\n"

                    else:
                        append_to_msg += "\nNot sent in an embed\n"

                    # Handle messages
                    msg = await self.len_or_sendbox(ctx, msg, append_to_msg)
                    append_to_msg = ""

            else:
                for name, alerts in alert_dict.items():
                    for num, alert in enumerate(alerts):

                        append_to_msg += "\n+ " + str(num) + ":" + name + "\nAlert text: " + alert['text']

                        if alert['channel'] is None:
                            append_to_msg += "\nChannel = DM"

                        else:
                            append_to_msg += "\nChannel = {}".format(ctx.guild.get_channel(alert['channel']).name)

                        if alert['em']:
                            append_to_msg += "\nSent in an embed\n"

                        else:
                            append_to_msg += "\nNot sent in an embed\n"

                        msg = await self.len_or_sendbox(ctx, msg, append_to_msg)
                        append_to_msg = ""

        await ctx.send("```diff\n" + msg + "```")

    async def len_or_sendbox(self, ctx, old_msg: str, append_msg: str):
        """Checks the length of the message and sends if the new message would be too long"""
        if len(old_msg + append_msg) > 1980:  # lenght plus box
            await ctx.send("```diff\n" + old_msg + "```")
            return append_msg

        else:
            return old_msg + append_msg

    @set_notification_roles.command(name="remove", no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove_roles(self, ctx, role_name):
        """Removes roles from notifications, use `[p]listroles` to find out what roles are set to be notifified"""

        # lists roles, Numbers are printed along side which are used as reference
        await ctx.send("Here are the list of Alerts set for this role:")
        message = ctx.message
        message.content = ctx.message.content.replace("remove", "list")
        await self.bot.process_commands(message)

        def check_author(msg):
            return msg.author == ctx.author

        async with self.Alerts.guild(ctx.guild).alerts() as alert_dict:

            await ctx.send("Enter a number to remove that alert")
            responce = await self.bot.wait_for("message", check=check_author, timeout=60)

            try:
                removed_alert = alert_dict[role_name][int(responce.content)]

            except:
                await ctx.send("That is not a valid input!")
                return

            await ctx.send(
                "This will remove the alert and people who gain this role will no longer be notified with this alert. \n\n__are you sure you want this? **y/n**__".format(
                    role_name))
            response = await self.bot.wait_for("message", check=check_author, timeout=60)

            if response is not None and 'y' in response.content.lower():
                alert_dict[role_name].remove(removed_alert)
                await ctx.send("Saved! -- Make sure to have a look at the documention on the git repo page!")

            else:
                await ctx.send("Aborted! --  Make sure to have a look at the documention on the git repo page!")

    @set_notification_roles.command(name="edit", no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def edit_roles(self, ctx, role_name):
        """Edits an alert"""

        # Actually just deletes the old alert and add the modifed one back in

        def check_author(msg):
            return msg.author == ctx.author

        await ctx.send("Which alert do you want to edit?")
        message = ctx.message
        message.content = ctx.message.content.replace("edit", "list")
        await self.bot.process_commands(message)

        async with self.Alerts.guild(ctx.guild).alerts() as alert_dict:

            await ctx.send("Enter a number to edit that alert")
            responce = await self.bot.wait_for("message", check=check_author, timeout=60)

            try:
                modifed_alert = alert_dict[role_name][int(responce.content)]

            except:
                await ctx.send("That is not a valid input!")
                return

            await ctx.send("Are you sure you want to edit this Alert? \n\n__are you sure you want this? **y/n**__")
            response = await self.bot.wait_for("message", check=check_author, timeout=120)

            if response is not None and 'y' in response.content.lower():
                await ctx.send(
                    "(timeout in 60 seconds, you can copy and paste a prepeared message)\n\nPlease enter new alert message: (let it time out if you would not like it to change)")
                response = await self.bot.wait_for("message", check=check_author, timeout=60)

                # create new alert
                if response is None:
                    message.content = ctx.message.content.replace("list", "add") + modified_alert['text']

                else:
                    message.content = ctx.message.content.replace("list", "add") + response.content

                await self.bot.process_commands(message)

                # delete old one
                alert_dict[role_name].remove(modifed_alert)
                await ctx.send("Saved!  --  Make sure to have a look at the documention on the git repo page!")

            else:
                await ctx.send("Aborted! --  Make sure to have a look at the documention on the git repo page!")