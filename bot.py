import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import json
import traceback
import os
from youtube_search import YoutubeSearch
intents = discord.Intents.all()
# client=discord.Client(intents=intents)
# intents.members=True
bot = commands.Bot(command_prefix='$',intents=intents)
@bot.event
async def on_ready():
    print('logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')
 # Customise the message below to what you want to send new users!

@bot.event
async def on_member_join(member):
    print("Recognised that a member called " + member.name + " joined")
    try: 
        await member.send("Have fun in the server!")
        print("Sent message to " + member.name)
    except:
        print("Couldn't message " + member.name)
        
    # role = discord.utils.get(member.server.roles, name="name-of-your-role") #  Gets the member role as a `role` object
    # await client.add_roles(member, role) # Gives the role to the user
    # print("Added role '" + role.name + "' to " + member.name)

@bot.event
async def on_member_remove(member):
    print("Recognised that a member called " + member.name + " left")
    try: 
        await member.send("Bye Bye!")
        print("Sent message to " + member.name)
    except:
        print("Couldn't message " + member.name)

@bot.command(name="ping",pass_context=True)
async def ping(ctx):
    print("Hi")
    await ctx.send("pong")

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', help='To play song')
async def play(ctx,url):
    search=url
    yt = YoutubeSearch(search, max_results=1).to_json()
    try:
        yt_id = str(json.loads(yt)['videos'][0]['id'])
        yt_url = 'https://www.youtube.com/watch?v='+yt_id
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(yt_url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        pass
        print(traceback.print_exc())
        print("no results")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

bot.run("Bot_Token") 