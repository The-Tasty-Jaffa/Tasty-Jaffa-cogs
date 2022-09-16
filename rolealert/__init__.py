"""RoleAlert cog (formaly Role Notifier). Notifies users with a message once a role has been gained."""

#Programed by The Tasty Jaffa
#2017 - present

from .rolenotifier import RoleNotifier


def setup(bot):
  this_cog = RoleNotifier(bot)

  #Data checking (ie cog was loaded or reloaded)

  #Listeners
  bot.add_listener(this_cog.role_update_check, 'on_member_update')

  bot.add_cog(this_cog)
