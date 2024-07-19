import discord
from discord.ext import commands
from discord import Intents, Embed
from discord.ui import Button, View
from urllib.parse import urlencode

intents = Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost:5000/callback'
AUTHORIZATION_BASE_URL = 'https://discord.com/api/oauth2/authorize'
SCOPE = ["identify", "email", "guilds.join", "guilds"]
ROLE_ID =   # 부여할 역할의 ID
CHANNEL_ID =   # 인증 링크를 게시할 채널의 ID
YOUR_GUILD_ID = 

class AuthButton(Button):
    def __init__(self):
        super().__init__(label="여기를 클릭하여 인증하세요", style=discord.ButtonStyle.link, url=get_auth_url())


def get_auth_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPE)
    }
    return f"{AUTHORIZATION_BASE_URL}?{urlencode(params)}"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return


    embed = Embed(title="인증하러가기", description="아래 버튼을 클릭하여 인증하세요", color=0x00ff00)
    button = AuthButton()
    view = View()
    view.add_item(button)
    
    await channel.send(embed=embed, view=view)
    print(f"Authentication link sent to channel {CHANNEL_ID}")

bot.run('')
