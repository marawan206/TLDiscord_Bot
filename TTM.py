import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
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

# Role IDs
ADMIN_ROLE_ID = <SPECIFY IF NEEDED>       # Normal Admin Role
HIGHER_ADMIN_ROLE_ID = <SPECIFY IF NEEDED>  # Higher Admin Role
MEMBER_ROLE_ID = <SPECIFY IF NEEDED>

# Announcement channel and Admin ID to be tracked by NLP
WATCHED_CHANNEL_ID = <SPECIFY IF NEEDED>
TARGET_USER_ID = <SPECIFY IF NEEDED>

# Channel IDs
TEXT_CHANNEL_ID = <SPECIFY IF NEEDED>
VOICE_CHANNEL_ID = <SPECIFY IF NEEDED>

# Load team data from a JSON file
def load_teams():
    try:
        with open("teams.json", "r", encoding="utf-8") as file:  # Specify UTF-8 encoding
            return json.load(file)
    except UnicodeDecodeError as e:
        print(f"Error loading teams.json: Encoding issue - {e}")
    except json.JSONDecodeError as e:
        print(f"Error loading teams.json: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error loading teams.json: {e}")
    return {}

teams = load_teams()

# Attendance data file
ATTENDANCE_FILE = "attendance.json"
     
# Run the bot
bot.run(TOKEN)
