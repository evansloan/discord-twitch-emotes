import os

import discord
from discord.ext import commands
from discord.utils import get

import emotes

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='+')
bot.remove_command('help')


@bot.command()
async def help(ctx):
    help_message = (
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
    embed = discord.Embed(colour=discord.Colour.green())
    embed.add_field(name='+add_emote', value=help_message)
    await ctx.send(embed=embed)


@bot.command()
async def add_emote(ctx, *, content: str):
    server = ctx.message.guild
    emote = emotes.get_emote(ctx, content)

    if not emote:
        await send_error(ctx, 'Invalid command')
        return

    if not emote.name or not emote.image:
        await send_error(ctx, 'Emote not found')
        return

    await server.create_custom_emoji(name=emote.name, image=emote.image.read())
    discord_emote = get(server.emojis, name=emote.name)
    await ctx.send(f'<:{discord_emote.name}:{discord_emote.id}> added!')


async def send_error(ctx, error):
    help_message = 'Type `+help` for further assistance'
    embed = discord.Embed(colour=discord.Colour.red())
    embed.add_field(name=f'Error: {error}', value=help_message)
    await ctx.send(embed=embed)


bot.run(token)
