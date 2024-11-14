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

# Announcement channel and David's ID
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

# Attendance data
attendance_data = load_attendance()

# Groq Client Setup
client = Groq(api_key=GROQ_API_KEY)

# Helper Function: Append events to schedule.json
def append_to_schedule(events):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        schedule = {}

        # Load existing schedule if file exists
        if os.path.exists("schedule.json"):
            with open("schedule.json", "r") as file:
                schedule = json.load(file)

        # Append events to today's schedule
        if today not in schedule:
            schedule[today] = []

        schedule[today].extend(events)

        # Save the updated schedule
        with open("schedule.json", "w") as file:
            json.dump(schedule, file, indent=4)
    except Exception as e:
        print(f"Error updating schedule.json: {e}")

# Helper Function: Process message with Groq API
def process_with_groq(message_content):
    try:
        # Send the message to Groq's LLM for processing
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": ("Extract structured event data from the following message. "
                                "Respond ONLY with a JSON array containing objects. Each object must have keys: "
                                "'name' (event title), 'time' (HH:MM), and 'description' (event details). "
                                "Do not include any other text or explanation in the response. "
                                f"Message: {message_content}")
                }
            ],
            model="llama3-8b-8192",
        )

        # Get the response and clean it
        response = chat_completion.choices[0].message.content
        print(f"Groq API Raw Response: {response}")  # Debug: Log the full response

        # Use regex to extract JSON from the response
        json_match = re.search(r"```(?:json)?\n([\s\S]*?)```", response)  # Matches JSON in code blocks
        if json_match:
            clean_json = json_match.group(1)
        else:
            clean_json = response.strip()  # Fallback: Assume response is already clean JSON

        print(f"Extracted JSON: {clean_json}")  # Debug: Log cleaned JSON
        return json.loads(clean_json)  # Parse the cleaned JSON
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw Response After Cleaning: {clean_json}")
    except Exception as e:
        print(f"Error processing message with Groq API: {e}")
    return []


# Event Listener: On Message
@bot.event
async def on_message(message):
    if message.channel.id == WATCHED_CHANNEL_ID and message.author.id == TARGET_USER_ID:
        print("Detected message from target user. Processing...")
        events = process_with_groq(message.content)
        
        # Debugging: Print extracted events
        print(f"Extracted events: {events}")

        if events:
            append_to_schedule(events)
            await message.channel.send("✅ Events successfully added to the schedule!")
        else:
            await message.channel.send("❌ Could not process the message or extract events.")
    
    # Process other commands
    await bot.process_commands(message)

    
# Helper function to check for admin role or higher admin role
def is_admin(ctx):
    admin_role = discord.utils.get(ctx.guild.roles, id=ADMIN_ROLE_ID)
    higher_admin_role = discord.utils.get(ctx.guild.roles, id=HIGHER_ADMIN_ROLE_ID)
    return admin_role in ctx.author.roles or higher_admin_role in ctx.author.roles


# Command: Show Commands List
@bot.command(name="commands")
async def show_commands(ctx):
    response = "**Available Commands:**\n\n"
    
    # General Commands
    response += "**General Commands:**\n"
    response += "**!commands** - Show this help message\n"
    response += "**!today** - Show today's scheduled events\n"
    response += "**!whois <username>** - Show the role and team of a user\n"
    response += "**!myteam** - Show your team's members\n"
    response += "**!myatt** - Show your personal attendance statistics\n"
    response += "**!allteams** - Show all teams and their members\n"
    response += "**!suggest** - Analyze teams and suggest fillers based on voice channel\n\n"
    
    # VOD Commands
    response += "**VOD Commands:**\n"
    response += "**!vodlink <vod_name> <link>** - Submit your VOD link\n"
    response += "**!listvods** - Show all available VODs and submission counts\n\n"
    
    # Admin Commands
    response += "**Admin Commands:**\n"
    response += "**!attendance [event_name]** - Record attendance from voice channel\n"
    response += "**!add <name> <time> [description]** - Add a new event\n"
    response += "**!details <username>** - Show detailed attendance for a user\n"
    response += "**!addvod <vod_name>** - Add a new VOD category\n"
    response += "**!vodinfo <vod_name>** - Show all submissions for a VOD\n\n"
    
    # Examples
    response += "**Examples:**\n"
    response += "`!whois KingTetrax`\n"
    response += "`!add \"Guild Event\" 19:00 Weekly guild meeting`\n"
    response += "`!vodlink \"Castle Siege 2024-01-10\" https://youtube.com/...`\n"
    
    await ctx.send(response)

# Run the bot
bot.run(TOKEN)
