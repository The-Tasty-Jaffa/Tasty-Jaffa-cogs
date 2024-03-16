"""Tempvoice allows for tempory channels to be created according to settings. These channels will be deleted after a set amount of time"""
import asyncio

from .tempvoice import TempVoice


async def setup(bot):
    temp_core = TempVoice(bot)

    loop = asyncio.get_event_loop()
    await loop.create_task(temp_core.voice_check())

    # Listeners
    # Thankyou to Tobotimus for giving a simple example on listeners
    bot.add_listener(temp_core.auto_voice, "on_voice_state_update")

    await bot.add_cog(temp_core)
