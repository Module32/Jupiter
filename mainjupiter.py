import discord, os, asyncio, random, sqlite3, datetime, praw, youtube_dl
from pretty_help import PrettyHelp
from discord.utils import get
from dotenv import load_dotenv
from discord.ext import commands, tasks
from random import choice

def get_prefix(bot, message):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT prefix FROM main WHERE guild_id = {message.guild.id}")
    prefix = cursor.fetchone()
    if prefix:
        if prefix[0]:
            prefix = prefix[0]
        else:
            prefix = "j!"
    else:
        prefix = "j!"
    db.close()
    return prefix

intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=PrettyHelp(active_time=120, color=0xf5b642, ending_note="j! help <command> for information about a command", show_index=False, page_left="⏪", page_right="⏩", remove="👍"))
load_dotenv()
TOKEN = os.getenv("JUPITER_TOKEN")

reddit = praw.Reddit(client_id = "QaiDh4StW-ZnAQ",
                     client_secret = "243ZQW8n6AhZ-MnxHCWjn3vHUW7u0Q",
                     username = "QuadCore24",
                     password = "Bab01234",
                     user_agent = "pythonpraw",
                     check_for_async=False)

subreddit = reddit.subreddit("memes")
top = subreddit.top(limit = 5)
eightballlist = ["It is certain", "It is decidedly so", "Without a doubt", "Yes, definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful", "Probably not", "I do not believe so", "Skeptical about that", "Seems unsure", "Absolutely not"]
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    """
    # use in future when adding new columns to table
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        ALTER TABLE main
        ADD COLUMN ticket_role_id
    ''')
    """
    print("Jupiter is ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="'j!help' | Version 1.0"))

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            joinchannelem = discord.Embed(title="👋 Hi there, I'm Jupiter! <:Jupiter_bot_pfp:836024171750096936>", description="📮 I'm a feature-rich bot with many applications and moderation features. The default prefix I use is `j!`. To get started using me, just send `j!help` in this channel and Jupiter will respond to you with commands you can use.\n\n🛡 Jupiter is a capable and extensive moderation bot. You can kick users, ban people, mute them, and do other things that allow you to protect your server and keep it safe against trolls.\n\n🌈 Jupiter is also customizable and able to fit your needs. You can change Jupiter's default prefix to your liking, set a channel to welcome new members when they join your server, and do even more with adaptive features.\n\nJupiter has even more, such as an economy system, fun commands, and utility commands. Thanks for inviting Jupiter! ♥", color=0xff91a4)
            joinchannelem.set_footer(text=f"{guild} • j!help", icon_url=f"{guild.icon_url}")
            await channel.send(embed=joinchannelem)
        break
    get_prefix()

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        if message.mention_everyone:
            pass
        else:
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT prefix FROM main WHERE guild_id = {message.guild.id}")
            prefix = cursor.fetchone()
            if prefix != None:
                await message.channel.send(f"**{message.author}**, use prefix `{prefix[0]}`")
            else:
                await message.channel.send(f"**{message.author}**, use prefix `j!`")
        if str(message.channel.type) == "private":
            modmail_channel = discord.utils.get(bot.get_all_channels(), name="mod-mail")
            if modmail_channel:
                await modmail_channel.send("")
            else:
                await message.guild.create_text_channel('mod-mail')
                # https://www.youtube.com/watch?v=MDrRQh0pY_s check modmail
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {before.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {before.guild.id}")
        result1 = cursor.fetchone()
        time = after.created_at
        if before.author.name == "Jupiter":
            pass
        else:
            messageeditem = discord.Embed(title=f"Message edited by **{before.author.name}** in **{before.channel}**", description=f"Edited at *{time}*", color=0xc8fa25)
            messageeditem.set_author(name=before.author.name, icon_url=before.author.avatar_url)
            messageeditem.add_field(name="Before:", value=f"`{before.content}`", inline=True)
            messageeditem.add_field(name="After:", value=f"`{after.content}`")
            if result[0]:
                channel = bot.get_channel(id=int(result[0]))
                await channel.send(embed=messageeditem)
            else:
                pass

@bot.event
async def on_message_delete(message: str):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {message.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {message.guild.id}")
        result1 = cursor.fetchone()
        if message.author.name == "Jupiter":
            pass
        else:
            messagedeleteem = discord.Embed(title=f"Message deleted by **{message.author.name}** in **{message.channel}**", description=f"Deleted at *{datetime.datetime.now()}*", color=0xc8fa25)
            messagedeleteem.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            messagedeleteem.add_field(name="Message:", value=f"`{message.content}`", inline=True)
            if result[0]:
                channel = bot.get_channel(id=int(result[0]))
                await channel.send(embed=messagedeleteem)
            else:
                pass

@bot.event
async def on_guild_role_create(role):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {role.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {role.guild.id}")
        result1 = cursor.fetchone()
        rolemadeem = discord.Embed(title=f"New role created in **{role.guild.name}**", description=f"Created at *{datetime.datetime.now()}*", color=0xc8fa25)
        rolemadeem.add_field(name="Role name:", value=f"`{role.name}`", inline=True)
        if result[0]:
            channel = bot.get_channel(id=int(result[0]))
            await channel.send(embed=rolemadeem)
        else:
            pass

@bot.event
async def on_guild_role_delete(role):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {role.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {role.guild.id}")
        result1 = cursor.fetchone()
        roledeleteem = discord.Embed(title=f"Role deleted in **{role.guild.name}**", description=f"Deleted at *{datetime.datetime.now()}*", color=0xc8fa25)
        roledeleteem.add_field(name="Role name:", value=f"`{role.name}`", inline=True)
        if result[0]:
            channel = bot.get_channel(id=int(result[0]))
            await channel.send(embed=roledeleteem)
        else:
            pass
            
@bot.event
async def on_guild_channel_update(before, after):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {before.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        if before.name != after.name:
            cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {before.guild.id}")
            result1 = cursor.fetchone()
            channelupdateem = discord.Embed(title=f"Channel changed in **{before.guild.name}**", description=f"Altered at *{datetime.datetime.now()}*", color=0xc8fa25)
            channelupdateem.add_field(name="Before:", value=f"`{before.name}`", inline=True)
            channelupdateem.add_field(name="After:", value=f"`{after.name}`", inline=True)
            if result[0]:
                channel = bot.get_channel(id=int(result[0]))
                await channel.send(embed=channelupdateem)
            else:
                pass
        else:
            pass

@bot.event
async def on_guild_channel_pins_update(channel, last_pin):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
        result1 = cursor.fetchone()
        channelmsgpinem = discord.Embed(title=f"Message pinned in **{channel.guild.name}**", description=f"Pinned in **#{channel}**", color=0xc8fa25)
        channelmsgpinem.add_field(name="Pinned at:", value=f"`{last_pin}`", inline=True)
        if result[0]:
            channel = bot.get_channel(id=int(result[0]))
            await channel.send(embed=channelmsgpinem)
        else:
            pass

@bot.event
async def on_member_join(member):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT welcome_channel_id FROM main WHERE guild_id = {member.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT welcome_msg FROM main WHERE guild_id = {member.guild.id}")
        result1 = cursor.fetchone()
        members = len(list(member.guild.members))
        mention = member.mention
        user = member.name
        guild = member.guild
        joinem = discord.Embed(title=str(result1[0]).format(members=members, mention=mention, user=user, guild=guild), description=f"**{member.guild}**", color=0x51f0cb)
        joinem.set_thumbnail(url=f"{member.avatar_url}")
        joinem.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
        joinem.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
        if result[0]:
            channel = bot.get_channel(id=int(result[0]))
        else:
            pass
        await channel.send(embed=joinem)

    cursor.execute(f"SELECT welcome_role_id FROM main WHERE guild_id = {member.guild.id}")
    result2 = cursor.fetchone()
    if result2:
        role = discord.utils.get(member.guild.roles, id=int(result2[0]))
        await member.add_roles(role)
    else:
        pass

@bot.event
async def on_member_remove(member):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT member_leave_channel_id FROM main WHERE guild_id = {member.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT member_leave_msg FROM main WHERE guild_id = {member.guild.id}")
        result1 = cursor.fetchone()
        members = len(list(member.guild.members))
        mention = member.mention
        user = member.name
        guild = member.guild
        leaveem = discord.Embed(title=str(result1[0]).format(members=members, mention=mention, user=user, guild=guild), description=f"**{member.guild}**", color=0xf54842)
        leaveem.set_thumbnail(url=f"{member.avatar_url}")
        leaveem.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
        leaveem.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
        if result:
            channel = bot.get_channel(id=int(result[0]))
        else:
            pass
        await channel.send(embed=leaveem)

@bot.event
async def on_guild_channel_create(channel):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
        result1 = cursor.fetchone()
        channelmakeem = discord.Embed(title=f"Channel created in **{channel.category}**", description=f"Created at *{datetime.datetime.now()}*", color=0xc8fa25)
        channelmakeem.add_field(name="Channel name:", value=f"`{channel}`", inline=True)
        channel = bot.get_channel(id=int(result[0]))
        await channel.send(embed=channelmakeem)

@bot.event
async def on_guild_channel_delete(channel):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
        result1 = cursor.fetchone()
        channelmakeem = discord.Embed(title=f"Channel deleted in **{channel.category}**", description=f"Deleted at *{datetime.datetime.now()}*", color=0xc8fa25)
        channelmakeem.add_field(name="Deleted channel's name:", value=f"`{channel}`", inline=True)
        channel = bot.get_channel(id=int(result[0]))
        await channel.send(embed=channelmakeem)

@bot.event
async def on_guild_channel_edit(channel):
    await channel.send("test")

@bot.event
async def on_guild_integrations_update(guild):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {guild.id}")
        result1 = cursor.fetchone()
        channelmakeem = discord.Embed(title=f"Integrations updated in **{guild}**", description=f"Integration set at *{datetime.datetime.now()}*", color=0xc8fa25)
        channel = bot.get_channel(id=int(result[0]))
        await channel.send(embed=channelmakeem)

@bot.event
async def on_webhooks_update(channel):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {channel.guild.id}")
        result1 = cursor.fetchone()
        channelmakeem = discord.Embed(title=f"Webhooks updated in **{channel}**", description=f"Webhooks updated at *{datetime.datetime.now()}*", color=0xc8fa25)
        channel = bot.get_channel(id=int(result[0]))
        await channel.send(embed=channelmakeem)

@bot.event
async def on_user_update(before, after):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT user_update_id FROM main WHERE guild_id = {before.guild.id}")
    result = cursor.fetchone()
    if result is None:
        return
    else:
        cursor.execute(f"SELECT user_update_id FROM main WHERE guild_id = {before.guild.id}")
        result1 = cursor.fetchone()
        memberupdateem = discord.Embed(title=f"{after.name} updated their profile", description=f"Updated at *{datetime.datetime.now()}*", color=0xc8fa25)
        memberupdateem.add_field(name="Before:", value=f"`{before}`", inline=True)
        memberupdateem.add_field(name="After:", value=f"`{after}`")
        memberupdateem.set_author(name=after.name, icon_url=after.avatar_url)
        if result:
            channel = bot.get_channel(id=int(result[0]))
            await channel.send(embed=memberupdateem)
        else:
            pass

@bot.group(invoke_without_command=True)
async def welcome(ctx):
    await ctx.send("**Welcome command configuration:**\n\nSet channel: `j!welcome channel <#channel>`\nSet text: `j!welcome text <text>`\nSet join role: `j!welcome role <@role>`\n\n*Note:* Command formatting can be used with this command.")

@bot.group(invoke_without_command=True)
async def prefix(ctx):
    await ctx.send("**Prefix command configuration:**\n\nSet new prefix: `j!prefix new <prefix>`")

@bot.group(invoke_without_command=True)
async def modlog(ctx):
    await ctx.send("**Modlogs command configuration:**\n\nSet modlogs channel: `j!modlog channel <#channel>`")

@bot.group(invoke_without_command=True)
async def memberleave(ctx):
    await ctx.send("**Member leave command configuration:**\n\nSet channel: `j!memberleave channel <#channel>`\nSet text: `j!memberleave text <text>`\n\n*Note:* Command formatting can be used with this command.")

@bot.group(invoke_without_command=True)
async def userupdate(ctx):
    await ctx.send("**User updates command configuration:**\n\nSet channel: `j!userupdate channel <#channel>`")

@bot.group(invoke_without_command=True)
async def editticket(ctx):
    await ctx.send("**Ticket command configuration:**\n\nSet text: `j!editticket text <text>`\nSet staff role: `j!editticket role <@role>`\n\n*Note:* Command formatting can be used with this command.")

@welcome.command()
async def channel(ctx, channel: discord.TextChannel):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_channel_id FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, welcome_channel_id) VALUES(?,?)")
            val = (ctx.guild.id, channel.id)
            welcomechannelsetem = discord.Embed(title=f"✅ **Welcome channel** has been set to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcomechannelsetem)
        elif result is not None:
            sql = ("UPDATE main SET welcome_channel_id = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            welcomechannelsetem = discord.Embed(title=f"✅ **Welcome channel** has been updated to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcomechannelsetem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@welcome.command()
async def text(ctx, *, text):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_msg FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, msg) VALUES(?,?)")
            val = (ctx.guild.id, text)
            welcometextsetem = discord.Embed(title=f"✅ **Welcome text** has been set to `{text}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcometextsetem)
        elif result is not None:
            sql = ("UPDATE main SET welcome_msg = ? WHERE guild_id = ?")
            val = (text, ctx.guild.id)
            welcometextsetem = discord.Embed(title=f"✅ **Welcome text** has been updated to `{text}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcometextsetem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@welcome.command()
async def role(ctx, *, role: discord.Role):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_role_id FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, welcome_role_id) VALUES(?,?)")
            val = (ctx.guild.id, role.id)
            welcomeroleem = discord.Embed(title=f"✅ **Welcome role** has been set to `{role}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcomeroleem)
        elif result is not None:
            sql = ("UPDATE main SET welcome_role_id = ? WHERE guild_id = ?")
            val = (role.id, ctx.guild.id)
            welcomeroleem = discord.Embed(title=f"✅ **Welcome role** has been updated to `{role}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=welcomeroleem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@prefix.command()
async def new(ctx, new_pr):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT prefix FROM main WHERE guild_id = {ctx.guild.id}")
        prefix = cursor.fetchone()
        if prefix is None:
            sql = ("INSERT INTO main(guild_id, prefix) VALUES(?,?)")
            val = (ctx.guild.id, new_pr)
            prefixsetem = discord.Embed(title=f"✅ **{ctx.guild.name}**'s prefix set to `{new_pr}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=prefixsetem)
        elif prefix is not None:
            sql = ("UPDATE main SET prefix = ? WHERE guild_id = ?")
            val = (new_pr, ctx.guild.id)
            prefixsetem = discord.Embed(title=f"✅ **{ctx.guild.name}**'s prefix updated to `{new_pr}`", description=f"Updated by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=prefixsetem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@modlog.command()
async def channel(ctx, channel: discord.TextChannel):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, modlog_channel) VALUES(?,?)")
            val = (ctx.guild.id, channel.id)
            modlogchannelsetem = discord.Embed(title=f"✅ **Modlog channel** has been set to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=modlogchannelsetem)
        elif result is not None:
            sql = ("UPDATE main SET modlog_channel = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            modlogchannelsetem = discord.Embed(title=f"✅ **Modlog channel** has been updated to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=modlogchannelsetem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@memberleave.command()
async def channel(ctx, channel: discord.TextChannel):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT member_leave_channel_id FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, member_leave_channel_id) VALUES(?,?)")
            val = (ctx.guild.id, channel.id)
            memberleavechannelsetem = discord.Embed(title=f"✅ **Member leave channel** has been set to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=memberleavechannelsetem)
        elif result is not None:
            sql = ("UPDATE main SET member_leave_channel_id = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            memberleavechannelem = discord.Embed(title=f"✅ **Member leave channel** has been updated to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=memberleavechannelem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@memberleave.command()
async def text(ctx, *, text):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT member_leave_msg FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, member_leave_msg) VALUES(?,?)")
            val = (ctx.guild.id, text)
            memberleavetextsetem = discord.Embed(title=f"✅ **Member leave text** has been set to `{text}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=memberleavetextsetem)
        elif result is not None:
            sql = ("UPDATE main SET member_leave_msg = ? WHERE guild_id = ?")
            val = (text, ctx.guild.id)
            memberleavetextsetem = discord.Embed(title=f"✅ **Member leave text** has been updated to `{text}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=memberleavetextsetem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@userupdate.command()
async def channel(ctx, channel: discord.TextChannel):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT user_update_id FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, user_update_id) VALUES(?,?)")
            val = (ctx.guild.id, channel.id)
            userupdatechannelem = discord.Embed(title=f"✅ **User profile update channel** has been set to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            userupdatechannelem.set_footer(text=f"{ctx.author.name} || careful with this one- it could be pretty spammy. Best practice, mute the channel under which the messages for user profile updates will come.", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=userupdatechannelem)
        elif result is not None:
            sql = ("UPDATE main SET user_update_id = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            userupdatechannelem = discord.Embed(title=f"✅ **User profile update channel** has been updated to `{channel}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            userupdatechannelem.set_footer(text=f"{ctx.author.name} || careful with this one- it could be pretty spammy. Best practice, mute the channel under which the messages for user profile updates will come.", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=userupdatechannelem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@editticket.command()
async def text(ctx, *, tickettext):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT ticket_text FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, ticket_text) VALUES(?,?)")
            val = (ctx.guild.id, tickettext)
            userupdatechannelem = discord.Embed(title=f"✅ **Ticket text** has been set to `{tickettext}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=userupdatechannelem)
        elif result is not None:
            sql = ("UPDATE main SET ticket_text = ? WHERE guild_id = ?")
            val = (tickettext, ctx.guild.id)
            userupdatechannelem = discord.Embed(title=f"✅ **Ticket text** has been updated to `{tickettext}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=userupdatechannelem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@editticket.command()
async def role(ctx, ticketrole: discord.Role):
    if ctx.message.author.guild_permissions.manage_messages:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT ticket_role_id FROM main WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO main(guild_id, ticket_role_id) VALUES(?,?)")
            val = (ctx.guild.id, ticketrole.id)
            userupdatechannelem = discord.Embed(title=f"✅ **Ticket role** has been set to `{ticketrole}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=userupdatechannelem)
        elif result is not None:
            sql = ("UPDATE main SET ticket_role_id = ? WHERE guild_id = ?")
            val = (ticketrole.id, ctx.guild.id)
            userupdatechannelem = discord.Embed(title=f"✅ **Ticket role** has been updated to `{ticketrole}`", description=f"Set by **{ctx.author}**", color=0x03fc45)
            await ctx.send(embed=userupdatechannelem)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f"🚫 **{ctx.author.name}**, you do not have the proper permissions to run that command!")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"🚫 **{ctx.author.name}**, I do not know what that command is!")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(f"🚫 **{ctx.author.name}**, that member could not be found!")
    elif isinstance(error, commands.MissingRequiredArgument):
        arg = error.param.name
        await ctx.send(f"`🚫 Following argument missing from your command: {arg} - type 'j!help' to learn more`")
    elif hasattr(error, "original"):
        raise error.original
    else:
        raise error


@bot.command(name="mute", help="Mutes a user so they cannot talk in the server anymore. Amount of time can be 'sec', 'min', or 'hrs'.")
@commands.has_permissions(manage_messages=True)
async def muteuser(ctx, user: discord.Member, time: int = None, timeval = None, *, reason = None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")
    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
    for channel in guild.channels:
      await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    if not user.bot:
        role = discord.utils.find(lambda r: r.name == 'Muted', ctx.message.guild.roles)
        if role in user.roles:
            await ctx.send(f"**{ctx.author.name}**, the user **{user}** is already muted! Unmute them with the `j!unmute <user> <reason: optional>` command.")
        else:
            if time:
                if timeval:
                    if timeval == "sec":
                        amttime = time
                    elif timeval == "min":
                        amttime = time * 60
                    elif timeval == "hrs":
                        amttime = (time * 60) * 60
                    else:
                        amttimeunknownem = discord.Embed(title=f"I do not know what the time value **{timeval}** is!", description="Enter 'sec', 'min', or 'hrs'.", color=0xff562b)
                        amttimeunknownem.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                        await ctx.send(embed=amttimeunknownem)
                        return
                    await user.add_roles(mutedRole)
                    tempmuteem = discord.Embed(title=f"**{user.display_name}** has been temporarily muted!", description=f"This user will be muted for {time} {timeval}.", color=0xff6e42)
                    tempmuteem.add_field(name="Information about mute", value=f"**By who:** {ctx.author.name}\n**On server:** *{guild}*", inline=True)
                    tempmuteem.add_field(name="Reason for mute:", value=f"*{reason}*")
                    await ctx.send(embed=tempmuteem)

                    await asyncio.sleep(amttime)
                    await user.remove_roles(mutedRole)
                    tempmuteem = discord.Embed(title=f"**{user.display_name}**'s temporary mute is over!", description=f"This user was muted for {time} {timeval}.", color=0x03fc6b)
                    tempmuteem.add_field(name="Information about mute", value=f"**By who:** {ctx.author.name}\n**On server:** *{guild}*", inline=True)
                    tempmuteem.add_field(name="Reason for mute:", value=f"*{reason}*")
                    await ctx.send(embed=tempmuteem)
            else:
                await user.add_roles(mutedRole)
                muteem = discord.Embed(title=f"**{user.display_name}** has been muted!", description="This user will be muted until you unmute them.", color=0xff6e42)
                muteem.add_field(name="Information about mute", value=f"**By who:** {ctx.author.name}\n**On server:** *{guild}*", inline=True)
                muteem.add_field(name="Reason for mute:", value=f"*{reason}*")
                await ctx.send(embed=muteem)

                mutedmem = discord.Embed(title=f"**{user}**, you were muted in *{guild}*!", description=f"*{ctx.author.name}* muted you.", color=0xff6e42)
                mutedmem.add_field(name=f"Reason: *{reason}*", value="Contact someone from the server who has the ability to unmute you to see if they can unmute you.")
                mutedmem = await user.send(embed=mutedmem)
    else:
        await ctx.send(f"**{ctx.author.name}**, *{user}* is a bot! You cannot mute people of my kind.")

@bot.command(name="unmute", help="Unmutes a user so they can talk in the server again.")
@commands.has_permissions(manage_messages=True)
async def muteuser(ctx, user: discord.Member, *, reason = None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")
    role = discord.utils.find(lambda r: r.name == 'Muted', ctx.message.guild.roles)
    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    if not user.bot:
        if role not in user.roles:
            await ctx.send(f"**{ctx.author.name}**, the user **{user}** is already unmuted! Mute them with the `j!mute <user> <reason: optional>` command.")
        else:
            await user.remove_roles(mutedRole)
            await ctx.send(f"**{user}** has successfully been unmuted by **{ctx.author.name}**!")

            unmutedmem = discord.Embed(title=f"**{user}**, you were unmuted in *{guild}*!", description=f"*{ctx.author.name}* unmuted you.", color=0x42f563)
            unmutedmem.add_field(name=f"Reason: *{reason}*", value="Mistakes happen; just try not to get yourself muted again in the future.", inline=True)
            unmutedmem = await user.send(embed=unmutedmem)
    else:
        await ctx.send(f"**{ctx.author.name}**, *{user}* is a bot! They were not muted in the first place.")

@bot.command(name="kick", help="Kicks a user from the server.")
async def kick(ctx, user: discord.User, *, reason = None):
    if user.id == 804777320123990108:
        await ctx.send(f"**{ctx.author.name}**, you cannot kick one of my creators!")
    elif user.id == 799835510956752926:
        await ctx.send(f"**{ctx.author.name}**, you cannot kick one of my creators!")
    elif user.id == 834843648901775390:
        await ctx.send(f"**{ctx.author.name}**, you cannot kick me!")
    else:
        kickdmem = discord.Embed(title=f"**{user}**, you were kicked from *{ctx.guild}* for `{reason}`.", color=0xff6e42)
        kickdmem.add_field(name="Information about kick", value=f"**By who:** {ctx.author.name}\n**On server:** *{ctx.guild}*", inline=True)
        kickdmem.set_footer(text="To enter the server again, contact someone in there or join again if it is a public server.")
        await user.send(embed=kickdmem)

        await ctx.guild.kick(user)

        kickem = discord.Embed(title=f"**{user}** was kicked from *{ctx.guild}*!", description=f"This user was kicked by **{ctx.author.name}**.", color=0xff4e33)
        kickem.add_field(name="Information about kick", value=f"**By who:** {ctx.author.name}\n**On server:** *{ctx.guild}*", inline=True)
        kickem.add_field(name="Reason for kick", value=reason)
        await ctx.send(embed=kickem)

@bot.command(name="ban", help="Bans a user from the server.")
async def ban(ctx, user: discord.User, *, reason = None):
    if user.id == 804777320123990108:
        await ctx.send(f"**{ctx.author.name}**, you cannot ban one of my creators!")
    elif user.id == 799835510956752926:
        await ctx.send(f"**{ctx.author.name}**, you cannot ban one of my creators!")
    elif user.id == 834843648901775390:
        await ctx.send(f"**{ctx.author.name}**, you cannot ban me!")
    else:
        bandmem = discord.Embed(title=f"**{user}**, you were banned from *{ctx.guild}* for `{reason}`.", color=0xff6e42)
        bandmem.add_field(name="Information about ban", value=f"**By who:** {ctx.author.name}\n**On server:** *{ctx.guild}*", inline=True)
        bandmem.set_footer(text="To enter the server again, contact someone in it to revoke your ban (if they have the permissions to).")
        await user.send(embed=bandmem)

        await ctx.guild.ban(user, reason=reason)

        banem = discord.Embed(title=f"**{user}** was banned from *{ctx.guild}*!", description=f"This user was banned by **{ctx.author.name}**.", color=0xff4e33)
        banem.add_field(name="Information about ban", value=f"**By who:** {ctx.author.name}\n**On server:** *{ctx.guild}*", inline=True)
        banem.add_field(name="Reason for ban", value=reason)
        banem.set_footer(text=f"To unban {user}, the ban must be revoked from server settings.")
        await ctx.send(embed=banem)

@bot.command(name="lock", help="Locks a channel.")
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel, *, reason = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    if reason == None:
        lockchannelem = discord.Embed(title=f"🔒 **{channel}** has been locked.", description=f"Locked by **{ctx.author}**", color=0xfca103)
    else:
        lockchannelem = discord.Embed(title=f"🔒 **{channel}** has been locked due to `{reason}`", description=f"Locked by **{ctx.author}**", color=0xfca103)
    await ctx.send(embed=lockchannelem)

@bot.command(name="unlock", help="Unlocks a channel.")
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel, *, reason = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    if reason == None:
        lockchannelem = discord.Embed(title=f"🔓 **{channel}** has been unlocked.", description=f"Unlocked by **{ctx.author}**", color=0xfca103)
    else:
        lockchannelem = discord.Embed(title=f"🔓 **{channel}** has been unlocked due to `{reason}`", description=f"Unlocked by **{ctx.author}**", color=0xfca103)
    await ctx.send(embed=lockchannelem)

@bot.command(name="slowmode", help="Sets a slowmode for a channel.")
async def slowmode(ctx, seconds: int):
    if seconds == 0:
        await ctx.channel.edit(slowmode_delay=0)
        slowmodesetem = discord.Embed(title=f"✅ Slowmode has been reset to 0 for **{channel}**", description=f"Reset by **{ctx.author}**", color=0x03fc45)
        await ctx.send(embed=slowmodesetem)
    else:
        await ctx.channel.edit(slowmode_delay=seconds)
        slowmodesetem = discord.Embed(title=f"✅ Slowmode has been set to `{seconds}` seconds for **{channel}**", description=f"Set by **{ctx.author}**", color=0x03fc45)
        await ctx.send(embed=slowmodesetem)

@bot.command(name="ping", help="Shows the bot's latency (its ping).")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    if latency <= 20:
        pingem = discord.Embed(title=f"✅ Great ping! Currently `{latency}`", color=0x03fc45)
    elif latency > 20 and latency < 50:
        pingem = discord.Embed(title=f"✅ Good ping! Currently `{latency}`", color=0x9dfc03)
    elif latency > 50 and latency < 70:
        pingem = discord.Embed(title=f"⚠ Lower ping. Currently `{latency}`", color=0xfce303)
    elif latency > 70:
        pingem = discord.Embed(title=f"❌ Terrible ping. Currently `{latency}`", color=0xfc2803)
    pingem.add_field(name="How it works", value="Latency is how much time it takes for a client to connect to some server. A lower latency generally means better in cases like Discord. 🏓")
    await ctx.send(embed=pingem)

@bot.command(name="invite", help="Sends the invite link for Jupiter so you can add it to other servers.")
async def invitelink(ctx):
    inviteem = discord.Embed(title="Invite link: **https://bit.ly/3nfldWY**", description="Clicking the link above will lead you to the invite.", color=0xfcb603)
    inviteem.set_footer(text="Thank you for inviting Jupiter! ♥      XOXO Jupiter's devs")
    await ctx.send(embed=inviteem)

@bot.command(name="play", help="Plays music in voice channels.")
async def play(ctx, url: str):
    pass

@bot.command(name="reddit", help="Shows a post from a subreddit. The default subreddit is set to r/memes.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def _reddit(ctx, subred = "memes"):
    subreddit = reddit.subreddit(subred)
    all_subs = []

    top = subreddit.top(limit = 50)
    for submission in top:
        all_subs.append(submission)

    random_sub = random.choice(all_subs)
    name = random_sub.title
    url = random_sub.url

    if submission.over_18:
        if ctx.channel.is_nsfw():
            memeem = discord.Embed(title = name, color=0xf7c41b)
            memeem.set_image(url=url)
            memeem.set_footer(text=f"NSFW - {ctx.author.name}", icon_url = ctx.author.avatar_url)
            await ctx.send(embed=memeem)
        else:
            await ctx.send(f"**{ctx.author.name}**, this is a *NSFW* channel! You cannot get posts from NSFW subreddits in this channel.")
    else:
        memeem = discord.Embed(title = name, color=0xf7c41b)
        memeem.set_image(url=url)
        memeem.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        await ctx.send(embed=memeem)

@bot.command(name="avatar", aliases=["pfp", "profilepic"], help="Shows the avatar/profile picture of a user.")
async def avatar(ctx, user: discord.Member = None):
    if user == None:
        avatarem = discord.Embed(title=f"Your profile picture, **{ctx.author.name}**")
        avatarem.set_image(url=ctx.author.avatar_url)
        avatarem.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = avatarem)
    else:
        avatarem = discord.Embed(title=f"**{user}**'s profile picture")
        avatarem.set_image(url=user.avatar_url)
        avatarem.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = avatarem)

@bot.command(name="8ball", aliases=["eightball", "8ba"], help="Rolls the magical 8-ball and gives you an answer.")
async def eightball(ctx, *, message: str):
    eightanswer = random.choice(eightballlist)
    eightem = discord.Embed(title=f"*{eightanswer}*", description=f"Original question: `{message}`", color=0x0033cc)
    eightem.add_field(name="Similar commands", value="`j!roll`, `j!flipacoin` - **j!help** to learn more")
    eightem.set_footer(text=f"Asked by {ctx.author}", icon_url=ctx.author.avatar_url)
    eightem.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/e/eb/Magic_eight_ball.png")
    await ctx.send(embed=eightem)

@bot.command(name="flipacoin", aliases=["headstails"], help="Flips a coin for you.")
async def flipacoin(ctx, side: str):
    if side == "heads" or side == "tails":
        sides = ["heads", "tails"]
        sidepick = random.choice(sides)
        result = ""
        if sidepick == side:
            result = "won!"
        else:
            result = "lost."
        coinem = discord.Embed(title=f"{sidepick} - You {result}", description=f"Your pick: **{side}** • Result: **{sidepick}**", color=0xDC7F64)
        coinem.add_field(name="Similar commands", value="`j!roll`, `j!8ball` - **j!help** to learn more")
        coinem.set_thumbnail(url="https://www.freepngimg.com/thumb/bitcoin/59787-cash-bitcoin-scalable-vector-graphics-logo.png")
        coinem.set_footer(text=f"Flipped by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=coinem)
    else:
        await ctx.send(f"**{ctx.author.name}**, that is not a valid side name!")

@bot.command(name="roll", aliases=["rolldice", "rollDice"], help="Rolls a dice for you. The first number is the number of dice, and the second is the number of sides.")
async def rollit(ctx, number_of_dice:int=1, number_of_sides:int=6):
  dice = [
    str(random.choice(range(1, number_of_sides + 1)))
    for _ in range(number_of_dice)
  ]
  diceem = discord.Embed(title="Result(s): " + ', '.join(dice), description="The amount of numbers is the number of dice you wanted.", color=0x854dff)
  diceem.set_thumbnail(url="http://www.clker.com/cliparts/f/9/a/f/1216179531563743945ytknick_A_die.svg.hi.png")
  diceem.add_field(name="Similar commands", value="`j!flipacoin`, `j!8ball` - **j!help** to learn more")
  diceem.set_footer(text=f"Rolled by {ctx.author.name}", icon_url = ctx.author.avatar_url)
  await ctx.send(embed=diceem)

@bot.command(name="ticket", help="Sets up a ticket so you can contact a server's staff members.")
async def openticket(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT ticket_text FROM main WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()
    userticket = discord.utils.get(bot.get_all_channels(), name=f"{ctx.author.name.lower()}-ticket")
    if userticket is not None:
        await ctx.send(f"**{ctx.author.name}**, you already have a ticket set up! Wait for someone to respond to it.")
    else:
        cursor.execute(f"SELECT ticket_role_id FROM main WHERE guild_id = {ctx.guild.id}")
        result1 = cursor.fetchone()
        role = ctx.guild.get_role(int(result1[0]))
        await ctx.message.delete()
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
            ctx.message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        name = f"{ctx.author.name}-ticket"
        channel = await ctx.message.guild.create_text_channel(name, overwrites=overwrites)
        desc = f"Someone will be here to assist you shortly.\nWhile you are here, please state your issue/problem."
        if result[0] is None:
            embed = discord.Embed(title=f"🎫 Thank you for contacting our staff.", description=f"Server: {ctx.guild}.", color=discord.Color.green())
        else:
            embed = discord.Embed(title=f"🎫 {result[0]}", description=f"Server: {ctx.guild}.", color=discord.Color.green())
        embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/thumbnails/000/376/226/small/Technical_Support.jpg")
        embed.set_footer(text=f"{ctx.author.name} - thanks to glizzybeam7801#8196 for help with the ticket system", icon_url=ctx.author.avatar_url)
        await channel.send(embed=embed)

@bot.command(name="closeticket", help="Closes the ticket that you had set up.")
async def closeticket(ctx):
    userticket = discord.utils.get(bot.get_all_channels(), name=f"{ctx.author.name.lower()}-ticket")
    if userticket:
            await userticket.delete()
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT modlog_channel FROM main WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                return
            else:
                ticketclosedem = discord.Embed(title=f"🎫 **{ctx.author.name}** closed their ticket.", description=f"Closed at {datetime.datetime.now()}.", color=0x21ffb1)
                ticketclosedem.set_author(name=f"Closed by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                channel = bot.get_channel(id=int(result[0]))
                await channel.send(embed=ticketclosedem)
    else:
        await ctx.send(f"**{ctx.author.name}**, you did not set up any ticket!")

@bot.command(name="logs", help="Sends the log files for Jupiter.")
async def logs(ctx):
    logfile = discord.File("C:\\Users\\admin\\Documents\\jupiterlogs.txt")
    logem = discord.Embed(title="Developer log files for Jupiter", description="The log files are sent as a .txt file. Download the attachment and open the file to see the logs.")
    logem.set_footer(text=f"{ctx.author.name} - {ctx.guild}", icon_url=ctx.author.avatar_url)
    await ctx.send(file=logfile, embed=logem)

bot.run(TOKEN)