import discord

# Discord
owner_ids = {123456789123456789, 987654321987654321}  # IDs of users with full permissions to control bot
discord_token = 'TOKEN'  # Create a new discord application, make a bot user, and copy the token at https://discordapp.com/developers/applications/
default_prefixes = {')'}  # Default bot prefix
color = 0xe3e3e3  # Color used to theme embeds
activity = discord.Activity(type=discord.ActivityType.watching, name=f'you! Default prefix: )')  # Activity shown by default
feedback_channel = 123456789123456789  # for feedback command
support_server = 123456789123456789  # for support server
created_on = 1573406528.783  # unix timestamp

# Wargaming
wg_token = 'TOKEN'  # Create a new application (mobile) and copy the ID at https://developers.wargaming.net/applications/.