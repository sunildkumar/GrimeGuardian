import asyncio
import discord
import os


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
            print("in loop for messaging")
            if not self.notification_queue.empty():
                message = self.notification_queue.get()
                fpath = "/Users/sunilkumar/Documents/GrimeGuardian/data_scraping/dirty_sink/000001.jpg"
                await channel.send(message, file=discord.File(fpath))
            await asyncio.sleep(5)
