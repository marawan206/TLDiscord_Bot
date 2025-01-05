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
ADMIN_ROLE_ID =        # Normal Admin Role
HIGHER_ADMIN_ROLE_ID =   # Higher Admin Role
MEMBER_ROLE_ID = 

# Announcement channel
WATCHED_CHANNEL_ID = 
TARGET_USER_ID = 

# Channel IDs
TEXT_CHANNEL_ID = 
VOICE_CHANNEL_ID = 

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

# Load attendance data from file# Load attendance data from file
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
    response = "**Available Commands:**\n"
    response += "**!commands** - Show this help message.\n"
    response += "**!attendance** - (Admins only) Show attendance summary.\n"
    response += "**!myteam** - Show your team's online members.\n"
    response += "**!add <name> <time (HH:MM)> [description]** - (Admins only) Add a new event.\n"
    response += "**!today** - Show today's scheduled events.\n"
    response += "**!whois <username>** - Show the role and team of a user.\n"
    response += "Example: `!whois john_doe`\n"
    await ctx.send(response)

# Command: Add a new event (Admins only)
@bot.command(name="add")
@commands.check(is_admin)
async def add_event(ctx, name: str = None, time: str = None, *, description: str = ""):
    if not name or not time:
        await ctx.send("❌ Usage: `!add <name> <time (HH:MM)> [description]`")
        return

    try:
        # Parse and save event
        event = {
            "name": name,
            "time": time,
            "description": description
        }
        with open("schedule.json", "r+") as file:
            schedule = json.load(file)
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in schedule:
                schedule[today] = []
            schedule[today].append(event)
            file.seek(0)
            json.dump(schedule, file, indent=4)

        await ctx.send(f"✅ Event '{name}' added for {time}!")
    except Exception as e:
        await ctx.send(f"❌ Failed to add event: {e}")

@add_event.error
async def add_event_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")

# Command: Show Attendance Summary (Admins only)
# Command: Record attendance
@bot.command(name="attendance")
@commands.check(is_admin)
async def attendance(ctx):
    guild = ctx.guild
    voice_channel = guild.get_channel(VOICE_CHANNEL_ID)

    if not voice_channel:
        await ctx.send("Voice channel not found! Check the channel ID.")
        return

    # Collect all attendees and sort alphabetically by display name
    attendees = sorted([member.display_name for member in voice_channel.members])

    # Save attendance to local data
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in attendance_data:
        attendance_data[today] = []
    attendance_data[today].extend(attendees)
    attendance_data[today] = list(set(attendance_data[today]))  # Remove duplicates
    save_attendance(attendance_data)

    # Send the list of attendees to the text channel
    response = "**Today's Attendance:**\n" + "\n".join(f"- {attendee}" for attendee in attendees) if attendees else "- None"
    text_channel = guild.get_channel(TEXT_CHANNEL_ID)
    if text_channel:
        await text_channel.send(response)
    await ctx.send("✅ Attendance recorded and posted to the text channel!")

@attendance.error
async def attendance_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")

# Command: Show User Role and Team
@bot.command(name="whois")
async def whois(ctx, *, nickname: str = None):
    if not nickname:
        await ctx.send("❌ Usage: `!whois <nickname>`")
        return

    # Special case for "user" 
    if nickname.lower() == "user":
        await ctx.send("Guild Leader")
        return

    user_role = None
    user_team = None
    member_found = False

    # Check for Discord nicknames or usernames
    for member in ctx.guild.members:
        if member.display_name.lower() == nickname.lower() or member.name.lower() == nickname.lower():
            member_found = True
            search_name = member.display_name
            break

    if not member_found:
        await ctx.send(f"❌ No member found with the nickname or username: **{nickname}**.")
        return

    # Search for user in team data
    for team, members in teams.items():
        for member in members:
            if member["name"].lower() == search_name.lower():
                user_role = member["role"]
                user_team = team
                break

    # Send user role and team info if found
    if user_role and user_team:
        response = f"**{search_name}** is a **{user_role}** and is currently assigned to **{user_team}**."
        if user_team == "Bombers":
            response += "\n**BOMBER GROUP** 💣"
        await ctx.send(response)
    else:
        await ctx.send(f"❌ No information found for **{search_name}**.")


# Command: Show Today's Events
@bot.command(name="today")
async def today(ctx):
    try:
        # Load schedule from file
        with open("schedule.json", "r") as file:
            schedule = json.load(file)

        # Define today's date in CET
        cet = pytz.timezone("CET")
        today_date = datetime.now(cet).strftime("%Y-%m-%d")

        if today_date not in schedule or not schedule[today_date]:
            await ctx.send("✅ No events scheduled for today.")
            return

        # Build the response message
        response = "**Today's Events (CET):**\n"
        for event in schedule[today_date]:
            response += f"- **{event['name']}**: {event['time']} | {event['description']}\n"

        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"❌ Error fetching today's events: {e}")

        
# Command: Show My Team
# Command: Show My Team
@bot.command(name="myteam")
async def myteam(ctx):
    user_name = ctx.author.display_name  # Use display name to match Discord nickname

    # Find the user's team
    user_team = None
    for team, members in teams.items():
        for member in members:
            if member["name"].lower() == user_name.lower():  # Case-insensitive check
                user_team = team
                break
        if user_team:
            break

    if not user_team:
        await ctx.send("❌ You are not assigned to any team.")
        return

    # Get all team members
    team_members = teams[user_team]
    all_members = [member["name"] for member in team_members]

    # Create response
    response = f"**Your Team:** {user_team}\n"
    response += f"**All Team Members:** {', '.join(all_members)}"

    # Add special message for Bombers
    if user_team == "Bombers":
        response += "\n**BOMBER GROUP** 💣"

    await ctx.send(response)
   
# Run the bot
bot.run(TOKEN)
