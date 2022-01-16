import os
import urllib.parse
from pytube import YouTube
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv


timeout_time = 10
error_message = "Ohh Vi irgendetwas ist schiefgelaufen."
client = discord.Client()
client = commands.Bot(command_prefix='!gi ')
client.remove_command('help')


async def dl_up_file(req, ctx, file_dir: str):
    """Downloads and uploads a file to the ctx channel.

    Args:
        req (requests.Response): The response with only the picture file as content.
        ctx: The context of the dl and upload.
        file_dir (str): File download path.
    """
    send_file = await dl_file(req, ctx, file_dir)
    await ctx.message.channel.send(file=send_file)


async def dl_file(req, ctx, file_dir: str):
    """Downloads a file.

    Args:
        req (requests.Response): The response with only the picture file as content.
        ctx: The context of the dl and upload.
        file_dir (str): File download path.
    """
    try:
        with open(file_dir, "wb") as f:
            f.write(req)
            print("file downloaded: " + file_dir)

            if os.path.getsize(file_dir) == 0:
                await  ctx.message.channel.send("Huh ein Fehler. Die Datei ist 0 byte groß?")
                print("Error file is 0 byte.")
                f.close()
            else:
                return discord.File(file_dir)
            f.close()

    except Exception.FileNotFoundError as e:
        print("File exception: " + e)


# @client.command(pass_context=True, name='join')
async def join(ctx):
    print("Connecting to voice...")
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        print("Connected.")
    else:
        print("User not found.")
        await ctx.message.channel.send("Du musst auch in einem Channel sein, du Vogel.")


# @client.command(pass_context=True, name='leave')
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.voice_client.disconnect()
    else:
        await ctx.message.channel.send("Ich bin nicht in einem Channel?")


# Help command

@client.command(pass_context=True, name='help')
async def help_bot(ctx):
    """Prints out a help string.

    Args:
        ctx (): Context of the message send.
    """
    
    author = ctx.message.author
    embed = discord.Embed(colour=discord.Colour.red())
    embed.set_author(name='Help')
    embed.add_field(name="Admin commands: ", value="`!gi purge x` Löscht x:int Nachrichten aus dem Kanal.", inline=True)
    embed.add_field(name="Casual commads: ", value="`!gi aiquote` Generiert ein schlechtes, motivierendes Bild.\n`!gi get x` Berechnet alles.", inline=True)
    await author.send(embed=embed)


# Casual commands

@client.command(pass_context=True, name="aiquote")
async def ai_quote(ctx):
    url = "https://inspirobot.me/api?generate=true"
    try:
        req = requests.get(url, timeout=timeout_time).text
        req = requests.get(req, timeout=timeout_time)
        print("Download from: {}".format(req.url))
        await dl_up_file(req.content, ctx, "dl\quote.jpg")
    except requests.exceptions.Timeout as e:
        print("Inspirobot can't be reached: " + e)
        await ctx.message.channel.send(error_message)


# FIXME this dosnt return anything when it takes too long.
@client.command(pass_context=True, name="get")
async def wolfram_compute(ctx, *, args="empty"):
    if args == "empty":
        await ctx.message.channel.send("Du solltest auch etwas wollen.\nVerwende den Befehl wie folgt:\t`!gi get x`\nwobei `x` alles sein kann. (Bevorzugt Mathezeugs)")
        return

    look_up = urllib.parse.quote(args)
    url_builder = f"http://api.wolframalpha.com/v1/simple?appid={os.getenv('APPID')}&i={look_up}"
    print("Using url in wolframalpha: {}".format(url_builder))

    try:
        req = requests.get(url_builder, timeout=timeout_time)
        print(req)
        await dl_up_file(req.content, ctx, "dl\wolfram.jpg")
    except requests.exceptions.Timeout as e:
        print("wolfram timeout: " + e)
        await ctx.message.channel.send(error_message)


# TODO Catch mistakes not url? name of vid should be enough!
# TODO Bot playback
@client.command(pass_context=True, name="play")
async def play_audio(ctx, url):
    await join(ctx)

    yt = YouTube(url)
    audio = yt.streams.get_audio_only()
    print(f"Downloading sound file {url}")
    audio.download(output_path="dl", filename="audio_file")
    print("Finished downloading.")

    ctx.voice_client.play(discord.FFmpegAudio(source="dl/audio_file.mp4"))


# Admin commands

@client.command(pass_context=True, name='purge')
async def purge(ctx, args="default"):
    if ctx.message.author.guild_permissions.administrator:
        print("args in purge: {}".format(args))
        try:
            limit = int(args) + 1
            print("amount to be purged: {}".format(limit))
        except ValueError as e:
            limit = 2
            print(e)

        async for messages in ctx.channel.history(limit=limit):
            await messages.delete()
    else:
        await ctx.message.channel.send("Böse! Nur Admins dürfen zensieren!")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.channel.send("Unbekannter Befehl tippe `!gi help` für hilfe.")


@client.event
async def on_ready():
    print("We have logged in as {}".format(client.user))
    await client.change_presence(status=discord.Status.online, activity=discord.Game("!gi help"))
    for guild in client.guilds:
        print("connected to: {}".format(guild.name))


# Run

def run_command_bot():
    load_dotenv()
    token = os.getenv('TOKEN')
    client.run(token)
