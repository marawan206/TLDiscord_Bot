import discord
from discord.ext import commands
from discord.ui import View, Button
import json
import os
from datetime import datetime
import pytz
from groq import Groq
import re

# Configuration
TOKEN = "your-discord-bot-token"
GROQ_API_KEY = "your-groq-api-key"
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Role and Channel IDs
ADMIN_ROLE_ID = <SPECIFY_IF_NEEDED>
HIGHER_ADMIN_ROLE_ID = <SPECIFY_IF_NEEDED>
MEMBER_ROLE_ID = <SPECIFY_IF_NEEDED>
WATCHED_CHANNEL_ID = <SPECIFY_IF_NEEDED>
TARGET_USER_ID = <SPECIFY_IF_NEEDED>
TEXT_CHANNEL_ID = <SPECIFY_IF_NEEDED>
VOICE_CHANNEL_ID = <SPECIFY_IF_NEEDED>

# Groq Client Setup
client = Groq(api_key=GROQ_API_KEY)

# Load team data
def load_teams():
    try:
        with open("teams.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (UnicodeDecodeError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading teams.json: {e}")
        return {}
teams = load_teams()

# Load attendance data
def load_attendance():
    try:
        with open("attendance.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
attendance_data = load_attendance()

# Button Menu for Commands
class CommandMenu(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Today's Events", style=discord.ButtonStyle.primary, custom_id="today_events"))
        self.add_item(Button(label="My Team", style=discord.ButtonStyle.secondary, custom_id="my_team"))
        self.add_item(Button(label="Attendance", style=discord.ButtonStyle.success, custom_id="attendance"))
        self.add_item(Button(label="VODs", style=discord.ButtonStyle.danger, custom_id="vods"))

@bot.command(name="menu")
async def show_menu(ctx):
    view = CommandMenu()
    await ctx.send("Choose an option:", view=view)

# Button Interaction Handling
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "today_events":
        await interaction.response.send_message("Fetching today's events...", ephemeral=True)
        await today(interaction)
    elif interaction.data["custom_id"] == "my_team":
        await interaction.response.send_message("Fetching your team info...", ephemeral=True)
        await myteam(interaction)
    elif interaction.data["custom_id"] == "attendance":
        await interaction.response.send_message("Checking attendance...", ephemeral=True)
        await attendance(interaction)
    elif interaction.data["custom_id"] == "vods":
        await interaction.response.send_message("Listing VODs...", ephemeral=True)
        await list_vods(interaction)

bot.run(TOKEN)
