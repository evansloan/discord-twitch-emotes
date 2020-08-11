import os

import discord
from discord.ext import commands
from discord.utils import get

import models
from emotes import Emote
from exceptions import EmoteNotFoundException, InvalidCommandException

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='+')
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('+help'))


@bot.command(aliases=['h'])
async def help(ctx):
    add_emote_msg = (
        'Adds a twitch emote to the server\n\n'
        '**Usage:**\n'
        '`+add_emote twitch <emote_id>`\n'
        '`+add_emote bttv <emote_id> <channel_name>`\n'
        '`+add_emote ffz <emote_id>`\n\n'
        'To get an emote visit [twitchemotes.com](https://twitchemotes.com), '
        '[betterttv.com](https://betterttv.com/emotes/shared), or '
        '[frankerfacez.com](https://www.frankerfacez.com/emoticons/) and find '
        'an emote of your liking.\n'
        'The channel name for BetterTTV emotes is found in the top right section '
        'of the web page for the emote\n'
        'The the ID of the emote is found at the end of the URL for a specific '
        'emote.\n'
        'twitchemotes.com/emotes/__**120232**__\n'
        'betterttv.com/emotes/__**5771aa498bbc1e572cb7ae4d**__\n'
        'frankerfacez.com/emoticon/__**261802**__-4Town'
    )
    emote_msg = (
        'Send an animated emote\n\n'
        '**Usage:**\n'
        '`+emote <emote_name>`\n\n'
        'Supply emote names as a comma-separated list to send multiple emotes in '
        'a single message'
    )
    embed = discord.Embed(colour=discord.Colour.green())
    embed.add_field(name='+add_emote', value=add_emote_msg)
    embed.add_field(name='+emote', value=emote_msg)
    await ctx.send(embed=embed)


@bot.command(aliases=['a'])
async def add_emote(ctx, *, content):
    server = ctx.message.guild

    try:
        emote = Emote.get_emote(content)
    except InvalidCommandException:
        await send_error(ctx, 'Invalid command')
        return
    except EmoteNotFoundException:
        await send_error(ctx, 'Emote not found')
        return

    await server.create_custom_emoji(name=emote.name, image=emote.image.read())
    discord_emote = get(server.emojis, name=emote.name)
    emote_string = f'<:{discord_emote.name}:{discord_emote.id}>'
    if discord_emote.animated:
        emote_string = f'<a:{discord_emote.name}:{discord_emote.id}>'
    await ctx.send(emote_string)


@bot.command(aliases=['e'])
async def emote(ctx, *, content):
    server = ctx.message.guild
    names = content.split(',')

    emote_string = ''
    for name in names:
        emote = get(server.emojis, name=name)
        if emote is None:
            await send_error(ctx, f'Emote {name} not found')
            return
        if emote.animated:
            emote_string += f'<a:{emote.name}:{emote.id}>'
        else:
            emote_string += f'<:{emote.name}:{emote.id}>'

    await ctx.send(emote_string)
    await ctx.message.delete()


@bot.command(aliases=['ac', 'ace'])
async def add_custom_emote(ctx, name, content):
    server = ctx.message.guild
    lines = content.split('/')
    emote_sets = []
    for line in lines:
        emote_sets.append(line.split(','))

    emote_string = ''
    for emote_set in emote_sets:
        for e in emote_set:
            emote = get(server.emojis, name=e.strip())
            if emote is None:
                await send_error(ctx, f'Emote {e} not found')
                return
            if emote.animated:
                emote_string += f'<a:{emote.name}:{emote.id}>'
            else:
                emote_string += f'<:{emote.name}:{emote.id}>'
        emote_string += '\n'

    ce = await models.CustomEmote.insert(name=name, emote_string=emote_string, server_id=server.id)
    
    await ctx.send(emote_string)
     

@bot.command(aliases=['c', 'ce'])
async def custom_emote(ctx, *, content):
    ce = await models.CustomEmote.select(name=content, server_id=ctx.message.guild.id)
    await ctx.send(ce.emote_string)


async def send_error(ctx, error):
    help_message = 'Type `+help` for further assistance'
    embed = discord.Embed(colour=discord.Colour.red())
    embed.add_field(name=f'Error: {error}', value=help_message)
    await ctx.send(embed=embed)


bot.loop.run_until_complete(models.create_db())
bot.run(token)
