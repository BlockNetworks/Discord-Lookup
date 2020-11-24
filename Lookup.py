#!/bin/env python3

from aiohttp import web
import asyncio
import discord
import json
import os
import threading
import time

class DiscordClient(discord.Client):
    ready = False

    async def on_ready(self):
        self.ready = True
        print(f'[INFO] Discord: logged in as {self.user}')

    def is_ready(self):
        return self.ready

async def fetch_by_id(request):
    uid = request.match_info["uid"]
    if not uid.isnumeric():
        return web.Response(text = json.dumps({error:"UID must be numeric"}))
    print("[INFO] fetchById: Searching for uid:", uid)
    discordUser = await client.fetch_user(uid)
    user = {
        "uid": discordUser.id,
        "tag": discordUser.name + "#" + discordUser.discriminator,
        "avatar": discordUser.avatar,
        "bot": discordUser.bot,
        "created_at": int(time.mktime(discordUser.created_at.timetuple()))
    }
    return web.Response(text = json.dumps(user))

async def handle_health(request):
    if not client.is_ready() or client.is_closed():
        return web.Response(text="no")
    return web.Response(text="yes")

async def alive(request):
    return web.Response(text="yes")

async def run_bot(token):
    await client.start(token)

def run_forever(loop):
    loop.run_forever()

token = os.environ['DISCORD_TOKEN']

client = DiscordClient()
loop = asyncio.get_event_loop()
loop.create_task(run_bot(token))

thread = threading.Thread(target=run_forever, args=(loop, ))

app = web.Application()
app.add_routes([web.get('/health', handle_health),
                web.get('/alive', alive),
                web.get('/by-uid/{uid}', fetch_by_id)])

web.run_app(app)

thread.join()
