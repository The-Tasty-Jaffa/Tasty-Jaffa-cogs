import discord
import asyncio, datetime
from redbot.core import Config, checks, commands


# Created by The Tasty Jaffa (2017-2018)
# Requested by idlechatter
# Improved by the comunity
# Thanks to Tobotimus for helping with the listener function

def get_role(ctx, role_id):
    roles = set(ctx.guild.roles)
    for role in roles:
        if role.id == role_id:
            return role
    return None


class TempVoice(commands.Cog):
    """Handles tempory channel settings for this cog"""

    __author__ = "The Tasty Jaffa"
    __version__ = "3.1.4"
    __email__ = "incoming+The_Tasty_Jaffa/Tasty-Jaffa-cogs@incoming.gitlab.com"

    def __init__(self, bot):
        self.bot = bot

        self.settings = Config.get_conf(self, identifier=42, force_registration=True)

        defualt_guild = {
            'role': None,
            'channel': None,
            'mode': False,
            'category': None,
            'defualt_name': "{user.display_name}",
        }
        # passwords, prv messages and the like should be handled by other applications

        defualt_global = {
            'check_empty': [],
        }

        self.settings.register_guild(**defualt_guild)
        self.settings.register_global(**defualt_global)

    # utils
    async def append_to_checks(self, channel_id: str):
        async with self.settings.check_empty() as check:
            check.append(channel_id)

    async def remove_from_checks(self, channel_id: str):
        async with self.settings.check_empty() as check:
            check.remove(channel_id)

    # Cog settings
    @commands.group(name="setvoice")
    @checks.admin_or_permissions(manage_channels=True)
    async def VoiceSet(self, ctx):  # Unchecked
        """Changes the settings for this cog, use with no sub command to get infomation on the cog and current setings"""

        if ctx.invoked_subcommand is None:
            em = discord.Embed(title="Tempary voice channel settings", description="""voice [name]
Creates a Voice channel named after the user who called it or by the optional parameter [name]
*only works when mode = 2*

*mode <mode_number>*
Sets the mode type for the server, defualts to 2.
When mode = 1, the cog will only permit the use of a Channel. `[p]setvoice mode 1`
When mode = 2, the cog will only permit the use of a command. `[p]setvoice mode 2`

*name <defualt_channel_name>*
Sets the defualt channel name format to be used when greating a channel
Use {user.display_name} for the users name
Use {user.activity} for the users current activity
Use {user.top_role.name} for name of the users highest role
see the d.py docs on `member` object for more detailed options
Also make sure I have "move members" and "manage channels" permissions! 

For more detail see the docs

__Current settings:__""", colour=0xff0000)
            guild_settings = self.settings.guild(ctx.guild)

            if await guild_settings.mode() is True:
                rep = "Use of a Channel (mode = 1)"
            else:
                rep = "Use of a Command (mode = 2)"

            em.add_field(name="Mode", value=rep, inline=False)

            try:
                em.add_field(name="Channel", value=ctx.guild.get_channel(await guild_settings.channel()).name,
                             inline=False)
            except:
                em.add_field(name="Channel", value="None", inline=False)

            try:
                em.add_field(name="Category", value=ctx.guild.get_channel(await guild_settings.category()).name,
                             inline=False)
            except:
                em.add_field(name="Category", value="None", inline=False)

            em.add_field(name="Role", value=get_role(ctx, await guild_settings.role()), inline=False)

            em.add_field(name="Name", value=await guild_settings.defualt_name())

            em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            em.set_footer(text="This cog can be found [here](https://github.com/The-Tasty-Jaffa/Tasty-Jaffa-cogs/)")

            await ctx.send(embed=em)

    @VoiceSet.command(name="category")
    @checks.admin_or_permissions(manage_channels=True)
    async def voice_set_category(self, ctx, category: discord.CategoryChannel = None):
        """Enter **Category** id - Sets the category that channels will be created under (don't enter anything to remove set category) (only has effect in mode = 2)"""

        if category is None:
            await self.settings.guild(ctx.guild).category.set(None)
            return

        await self.settings.guild(ctx.guild).category.set(category.id)
        await ctx.send(
            "Category set as {0}! New channels will be created here if a command is used".format(category.name))

    @VoiceSet.command(name="channel")
    @checks.admin_or_permissions(manage_channels=True)
    async def voice_set_channel(self, ctx, channel: discord.VoiceChannel = None):  # To do
        """Enter *Voice channel ID* to set the channel to join to make a tempory channel (Mode must be = 1). Don't enter anything to remove set channel"""

        if channel is None:
            await self.settings.guild(ctx.guild).channel.set(None)
            return

        await ctx.send("Channel set!")
        await self.settings.guild(ctx.guild).channel.set(channel.id)

    @VoiceSet.command(name="role")
    @checks.admin_or_permissions(manage_channels=True)
    async def voice_set_role(self, ctx, role_name: str = ""):
        """sets the required role to use the [p]voice command (leave blank for no role)"""

        role = discord.utils.get(ctx.message.server.roles, name=role_name)

        if role_name == "":
            await ctx.send("The requirement of having a role has been removed!")
            await self.settings.guild(ctx.guild).role.set(None)
            return

        if role is None:
            await ctx.send("Sorry but that role could not be found")
            return

        await ctx.send("Role set!")
        await self.settings.guild(ctx.guild).role.set(role.id)

    @VoiceSet.command(name="mode")
    @checks.admin_or_permissions(manage_channels=True)
    async def voice_set_type(self, ctx, voice_mode: int):
        """Sets the Voice channel creation type - [2] = use of command - [1] = Use of channel"""

        if voice_mode == 2:
            await self.settings.guild(ctx.guild).mode.set(False)
            await ctx.send("Mode changed to use of a command `[p]voice` [Mode = 2]")

        elif voice_mode == 1:
            await self.settings.guild(ctx.guild).mode.set(True)
            await ctx.send("Mode changed to use of a channel `Join the set channel` [Mode = 1]")

        else:
            await ctx.send("Sorry that's not a valid type")

    @VoiceSet.command(name="name")
    @checks.admin_or_permissions(manage_channels=True)
    async def voice_set_default(self, ctx, *, defualt_name: str = "{user.display_name}"):
        """sets the default channel name, resets with no parameters"""

        await self.settings.guild(ctx.guild).defualt_name.set(defualt_name)
        await ctx.send("Default channel name set to `{0}`!".format(defualt_name))

    # Voice command
    # @tempvoice.event(name="channel_created")
    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def voice(self, ctx, *, name: str = ''):  # actual command
        """Creates a voice channel use opptional argument <name> to spesify the name of the channel, Use `" "` around the name of the channel"""
        guild_settings = self.settings.guild(ctx.guild)
        # Checks the mode (type = True (therefore mode = 1 = channel)
        if await guild_settings.mode() is True:
            return

        # Check role
        server_role = await guild_settings.role()
        if server_role is not None:
            for role in set(ctx.author.roles):
                if role.id == server_role:
                    break  # If role is found

            else:  # If we didn't break out of the loop then the user does not have the right role
                await ctx.send("Sorry but you are not permited to use that command! A role is needed.")
                return  # If role is found breaks loop - else statement isn't executed.

        # Handle naming
        if name == '':  # Tests if no name was passed
            name = await guild_settings.defualt_name()
            if ctx.author.activity is None:
                name = name.replace("{user.activity}", "Nothing")  # Replaces "None" so that channel name reads better
            name = name.format(user=ctx.author)

        # If all the requirements are met
        try:
            # perms = discord.PermissionOverwrite(manage_channels=True)#Sets permisions
            # perms = discord.ChannelPermissions(target=ctx.author, overwrite=perms)#Sets the channel permissions for the person who sent the message
            channel = await ctx.guild.create_voice_channel(name, category=ctx.guild.get_channel(
                await guild_settings.category()), reason="Creating a temp channel")  # creates a channel
            await channel.set_permissions(ctx.author, manage_channels=True)  # allows them to manage the temp channel

            await self.append_to_checks(channel.id)
            return True

        except discord.Forbidden:
            await ctx.send("I don't have the right perrmissions for that! (I need to be able to manage channels)")

        except Exception as e:  # if something else happens such as it's not connected or a file has been messed with and so doesn't show an error in discord channel
            print("=================")
            print(e)
            print("=================")

            await ctx.send("An error occured - check logs")

    # @event(name="channel_created")
    async def auto_voice(self, member, before, after):  # Is called when Someone joins the voice channel - Listener
        """Automaticly checks the voice channel for users and makes a channel for them"""

        guild_settings = self.settings.guild(member.guild)

        # Deletion of channels
        # I cannot have any returns here so channels will be created
        if before.channel is not None:
            # Did they come from a channel?

            if before.channel.id in await self.settings.check_empty():
                # Was the channel they where in a tempary channel?

                if len(before.channel.members) == 0:
                    # How many people are in the channel?
                    # if zero => empty. Therefore, remove the channel
                    await before.channel.delete(reason="Removing empty temp channel")
                    await self.remove_from_checks(before.channel.id)

        # Creation of channel
        # Are they in a channel right now?
        if after.channel is None:
            return

        # Is it in the right mode?
        if await guild_settings.mode() != True:
            return

        try:
            if await guild_settings.channel() != after.channel.id:
                return

            # Channel naming
            name = await guild_settings.defualt_name()

            if member.activity is None:
                name = name.replace("{user.activity}", "Nothing")  # Replaces "None" so that channel name reads better

            name = name.format(user=member)

            # Channel creation
            position = after.channel.position

            channel = await member.guild.create_voice_channel(name, category=after.channel.category,
                                                              reason="Creating a temp channel")
            await channel.set_permissions(member, manage_channels=True)  # allows them to manage the temp channel

            await self.append_to_checks(channel.id)

            await member.move_to(channel, reason="User created a temp channel, moving them to their temp channel")
            await channel.edit(position=position + 1, reason="Moving tmp channel under tmp channel spawn")

        except discord.Forbidden:
            await member.guild.owner.send(
                "I need the proper permissions! I was unable to create a new channel. (Move members, Manage channels)")

    # @listen.timer(60)
    async def voice_check(self):  # Loops around until channel is empty
        DELAY = 60  # Delay in seconds

        while self == self.bot.get_cog("TempVoice"):  # While bot is online/cog is loaded

            async with self.settings.check_empty() as check_empty:
                channels_to_remove = []
                for channel_id in check_empty:

                    # So it doesn't go "Oh this channel doesn't exist" (becuase the bot isn't online/logged on)
                    if self.bot.is_closed() is True:
                        continue

                    current = self.bot.get_channel(channel_id)

                    if current is None:  # if channel doesn't exist
                        Channels_to_remove.append(channel_id)
                        continue

                    # Is the channel Empty (returns empty list if empty)
                    if len(current.members) != 0:
                        continue

                    if datetime.datetime.today() - datetime.timedelta(seconds=15) < current.created_at:
                        continue

                    await current.delete(reason="Deleting empty/unused tmp channel")
                    channels_to_remove.append(channel_id)  # Adds it to a list for removal

                for channel_id in channels_to_remove:
                    check_empty.remove(channel_id)

            await asyncio.sleep(DELAY)
