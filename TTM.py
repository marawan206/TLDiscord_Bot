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

# Load attendance data from file
def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        try:
            with open(ATTENDANCE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in attendance file.")
    return {}


# Save attendance data to file
def save_attendance(event_name, attendees):
    try:
        # Load existing attendance data
        with open("attendance.json", "r", encoding="utf-8") as file:
            attendance_data = json.load(file)
    except FileNotFoundError:
        attendance_data = {}  # Initialize if file doesn't exist

    # Get today's date as a string
    today = datetime.now().date().isoformat()

    # Ensure the date exists in the data
    if today not in attendance_data:
        attendance_data[today] = {}

    # Save the event's attendance
    attendance_data[today][event_name] = {
        "time": datetime.now().strftime("%H:%M"),
        "attendees": attendees
    }

    # Write the updated data back to the file
    with open("attendance.json", "w", encoding="utf-8") as file:
        json.dump(attendance_data, file, indent=4, ensure_ascii=False)
     
# Run the bot
bot.run(TOKEN)
