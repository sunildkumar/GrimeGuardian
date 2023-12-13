import asyncio
from thread_safe_state import StateModel
import discord
import os

DEFAULT_MESSAGE = "Alert! The sink is staging a dirty dishes rebellion. Time to restore order! Troops, to the kitchen!"


class DiscordBot(discord.Client):
    def __init__(self, notification_queue, stop_event, *args, **kwargs):
        intents = discord.Intents.default()
        super().__init__(intents=intents, *args, **kwargs)
        self.notification_queue = notification_queue
        self.stop_event = stop_event
        self.channel_id = os.getenv("CHANNEL_ID")

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(int(self.channel_id))
        while not self.stop_event.is_set():
            if not self.notification_queue.empty():
                state: StateModel = self.notification_queue.get()
                iq_id = state.sink_state_iq_id
                fpath = f"../data/{iq_id}.jpg"
                await channel.send(DEFAULT_MESSAGE, file=discord.File(fpath))
            await asyncio.sleep(5)
