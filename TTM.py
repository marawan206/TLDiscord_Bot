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
@commands.check(is_admin)  # Ensure this decorator is applied
async def attendance(ctx, *, event_name: str = "default"):
    # Get the voice channel
    guild = ctx.guild
    voice_channel = guild.get_channel(VOICE_CHANNEL_ID)

    if not voice_channel:
        await ctx.send("❌ Voice channel not found! Check the channel ID.")
        return

    # Get attendees in the voice channel
    attendees = sorted([member.display_name for member in voice_channel.members])
    if not attendees:
        await ctx.send("❌ No attendees found in the voice channel.")
        return

    # Save attendance to JSON file
    save_attendance(event_name, attendees)
    
    # Respond with attendance details
    attendee_count = len(attendees)
    attendee_list = ', '.join(attendees)
    await ctx.send(
        f"✅ Attendance for event '{event_name}' has been recorded!\n"
        f"**Total Attendees:** {attendee_count}\n"
        f"**Attendees:** {attendee_list}"
    )

# Handle errors for the attendance command
@attendance.error
async def attendance_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Command: Show User Role and Team
@bot.command(name="whois")
async def whois(ctx, *, nickname: str = None):
    if not nickname:
        await ctx.send("❌ Usage: `!whois <nickname>`")
        return

    # Special case for "SPECIAL" 
    if nickname.lower() == "SPECIAL":
        await ctx.send("REAL GIGACHAD\nhttps://tenor.com/view/gigachad-chad-gif-20773266")
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
    
# Command: Check personal attendance
@bot.command(name="myatt")
async def my_attendance(ctx):
    user_name = ctx.author.display_name
    try:
        # Load attendance data
        with open("attendance.json", "r", encoding="utf-8") as file:
            attendance_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("No attendance records found.")
        return

    # Get the dates from your attendance data
    dates = sorted(list(attendance_data.keys()))
    if not dates:
        await ctx.send("No attendance records found.")
        return

    # Get the most recent date
    latest_date = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    
    # Calculate week ranges based on the latest date
    start_of_this_week = latest_date - timedelta(days=latest_date.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)
    
    days_this_week = [(start_of_this_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    days_last_week = [(start_of_last_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    def calculate_attendance(days):
        total_events = 0
        attended_events = 0
        missed_events = []

        for day in days:
            if day in attendance_data:
                for event, details in attendance_data[day].items():
                    total_events += 1
                    if user_name in details["attendees"]:
                        attended_events += 1
                    else:
                        missed_events.append(f"**{event}** at {details['time']} on {day}")
            else:
                missed_events.append(f"**No events recorded on {day}**")

        attendance_percentage = (attended_events / total_events) * 100 if total_events > 0 else 0
        return {
            "total_events": total_events,
            "attended_events": attended_events,
            "attendance_percentage": attendance_percentage,
            "missed_events": "\n".join(missed_events) if missed_events else "None",
        }

    # Calculate attendance for this week and last week
    this_week_data = calculate_attendance(days_this_week)
    last_week_data = calculate_attendance(days_last_week)

    # Format responses for this week and last week
    this_week_response = (
        f"**This Week's Attendance Details:**\n"
        f"Attendance Rate: **{this_week_data['attendance_percentage']:.2f}%**\n"
        f"Total Events Attended: **{this_week_data['attended_events']}/{this_week_data['total_events']}**\n\n"
        f"**Missed Events and Days:**\n{this_week_data['missed_events']}\n\n"
        if this_week_data["total_events"] > 0
        else "**This Week's Attendance Details:**\nNo attendance recorded this week yet.\n\n"
    )

    last_week_start_date = start_of_last_week.strftime("%Y-%m-%d")
    last_week_response = (
        f"**Last Week's Attendance Details (Week of {last_week_start_date}):**\n"
        f"Attendance Rate: **{last_week_data['attendance_percentage']:.2f}%**\n"
        f"Total Events Attended: **{last_week_data['attended_events']}/{last_week_data['total_events']}**\n\n"
        f"**Missed Events and Days:**\n{last_week_data['missed_events']}\n\n"
        if last_week_data["total_events"] > 0
        else f"**Last Week's Attendance Details (Week of {last_week_start_date}):**\nNo attendance recorded last week.\n\n"
    )

    # Prepare the full response
    response = f"{this_week_response}{last_week_response}"

    # Send the response
    await ctx.send(response)
    
@bot.command(name="details")
@commands.has_permissions(administrator=True)
async def details(ctx, discord_name: str):
    try:
        # Load attendance data
        with open("attendance.json", "r", encoding="utf-8") as file:
            attendance_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("No attendance records found.")
        return

    try:
        # Load team data
        with open("teams.json", "r", encoding="utf-8") as file:
            teams_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("No team records found.")
        return

    # Find the user's team and role
    user_team = "Not assigned"
    user_role = "Not assigned"
    for team, members in teams_data.items():
        for member in members:
            if member["name"].lower() == discord_name.lower():
                user_team = team
                user_role = member["role"]
                break
        if user_team != "Not assigned":
            break

    # Get the dates from your attendance data
    dates = sorted(list(attendance_data.keys()))
    if not dates:
        await ctx.send("No attendance records found.")
        return

    # Get the most recent date
    latest_date = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    
    # Calculate week ranges based on the latest date
    start_of_this_week = latest_date - timedelta(days=latest_date.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)
    
    days_this_week = [(start_of_this_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    days_last_week = [(start_of_last_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    def calculate_attendance(days):
        total_events = 0
        attended_events = 0
        missed_events = []
        missed_days = set(days)

        for day in days:
            if day in attendance_data:
                for event, details in attendance_data[day].items():
                    total_events += 1
                    if discord_name in details["attendees"]:
                        attended_events += 1
                        if day in missed_days:
                            missed_days.remove(day)
                    else:
                        missed_events.append(
                            f"**{event}** at {details['time']} on {day}"
                        )

        missed_days_list = "\n".join(missed_days) if missed_days else "None"
        missed_events_list = "\n".join(missed_events) if missed_events else "None"
        attendance_percentage = (attended_events / total_events) * 100 if total_events > 0 else 0

        return {
            "total_events": total_events,
            "attended_events": attended_events,
            "attendance_percentage": attendance_percentage,
            "missed_days": missed_days_list,
            "missed_events": missed_events_list,
        }

    # Calculate attendance for this week and last week
    this_week_data = calculate_attendance(days_this_week)
    last_week_data = calculate_attendance(days_last_week)

    # Format responses for this week and last week
    this_week_response = (
        f"**This Week's Attendance Details:**\n"
        f"Attendance Rate: **{this_week_data['attendance_percentage']:.2f}%**\n"
        f"Total Events Attended: **{this_week_data['attended_events']}/{this_week_data['total_events']}**\n\n"
        f"**Missed Days:**\n{this_week_data['missed_days']}\n\n"
        f"**Missed Events:**\n{this_week_data['missed_events']}\n\n"
        if this_week_data["total_events"] > 0
        else "**This Week's Attendance Details:**\nNo attendance recorded this week yet.\n\n"
    )

    last_week_start_date = start_of_last_week.strftime("%Y-%m-%d")
    last_week_response = (
        f"**Last Week's Attendance Details (Week of {last_week_start_date}):**\n"
        f"Attendance Rate: **{last_week_data['attendance_percentage']:.2f}%**\n"
        f"Total Events Attended: **{last_week_data['attended_events']}/{last_week_data['total_events']}**\n\n"
        f"**Missed Days:**\n{last_week_data['missed_days']}\n\n"
        f"**Missed Events:**\n{last_week_data['missed_events']}\n\n"
        if last_week_data["total_events"] > 0
        else f"**Last Week's Attendance Details (Week of {last_week_start_date}):**\nNo attendance recorded last week.\n\n"
    )

    # Prepare the response
    response = (
        f"**Details for {discord_name}:**\n"
        f"Team: **{user_team}**\n"
        f"Role: **{user_role}**\n\n"
        f"{this_week_response}"
        f"{last_week_response}"
    )

    # Send the response
    await ctx.send(response)
    
    
    
"""
NEW SECTIONS
"""

# Helper functions for VOD management
def load_vod_data():
    try:
        with open("vods.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"vod_names": [], "vod_links": {}}

def save_vod_data(data):
    with open("vods.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Command to add a new VOD name (admin only)
@bot.command(name="addvod")
@commands.check(is_admin)
async def add_vod(ctx, *, vod_name: str):
    vod_data = load_vod_data()
    
    # Convert to lowercase for case-insensitive comparison
    vod_name_lower = vod_name.lower()
    
    # Check if VOD name already exists
    if vod_name_lower in [name.lower() for name in vod_data["vod_names"]]:
        await ctx.send(f"❌ VOD name '{vod_name}' already exists!")
        return
    
    # Add new VOD name
    vod_data["vod_names"].append(vod_name)
    vod_data["vod_links"][vod_name] = {}
    save_vod_data(vod_data)
    
    await ctx.send(f"✅ Added new VOD name: **{vod_name}**")

@add_vod.error
async def add_vod_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: !addvod <vod_name>")

# Command for members to add their VOD links
@bot.command(name="vodlink")
async def add_vod_link(ctx, vod_name: str, link: str):
    vod_data = load_vod_data()
    
    # Convert to lowercase for case-insensitive comparison
    vod_name_lower = vod_name.lower()
    
    # Find the actual VOD name with correct case
    actual_vod_name = None
    for name in vod_data["vod_names"]:
        if name.lower() == vod_name_lower:
            actual_vod_name = name
            break
    
    if not actual_vod_name:
        # List available VOD names if the provided name doesn't exist
        vod_list = "\n".join(vod_data["vod_names"]) if vod_data["vod_names"] else "No VODs available"
        await ctx.send(f"❌ Invalid VOD name. Available VODs:\n{vod_list}")
        return
    
    # Validate URL format (basic check)
    if not link.startswith(('http://', 'https://')):
        await ctx.send("❌ Invalid link format. Link must start with http:// or https://")
        return
    
    # Add or update the member's VOD link
    vod_data["vod_links"][actual_vod_name][ctx.author.display_name] = link
    save_vod_data(vod_data)
    
    await ctx.send(f"✅ Added your VOD link for **{actual_vod_name}**")

@add_vod_link.error
async def add_vod_link_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: !vodlink <vod_name> <link>")

# Command to list all VODs and their statistics
@bot.command(name="listvods")
async def list_vods(ctx):
    vod_data = load_vod_data()
    
    if not vod_data["vod_names"]:
        await ctx.send("No VODs available.")
        return
    
    response = "**Available VODs and Submissions:**\n\n"
    
    for vod_name in vod_data["vod_names"]:
        link_count = len(vod_data["vod_links"].get(vod_name, {}))
        response += f"**{vod_name}** - {link_count} submissions\n"
    
    await ctx.send(response)

# Command to view detailed VOD information (admin only)
@bot.command(name="vodinfo")
@commands.check(is_admin)
async def vod_info(ctx, *, vod_name: str):
    vod_data = load_vod_data()
    
    # Convert to lowercase for case-insensitive comparison
    vod_name_lower = vod_name.lower()
    
    # Find the actual VOD name with correct case
    actual_vod_name = None
    for name in vod_data["vod_names"]:
        if name.lower() == vod_name_lower:
            actual_vod_name = name
            break
    
    if not actual_vod_name:
        await ctx.send(f"❌ VOD name '{vod_name}' not found!")
        return
    
    links = vod_data["vod_links"].get(actual_vod_name, {})
    
    if not links:
        await ctx.send(f"No submissions for **{actual_vod_name}**")
        return
    
    response = f"**VOD Links for {actual_vod_name}:**\n\n"
    for member, link in links.items():
        response += f"**{member}**: {link}\n"
    
    await ctx.send(response)

@vod_info.error
async def vod_info_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: !vodinfo <vod_name>")
        
"""
New section 2
"""

@bot.command(name="allteams")
async def all_teams(ctx):
    try:
        with open("teams.json", "r", encoding="utf-8") as file:
            teams_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("❌ Error loading teams data.")
        return

    response = "**Current Teams Setup:**\n\n"
    
    # Process main teams first
    for team_name, members in teams_data.items():
        if team_name == "Fillers":
            continue
            
        response += f"**{team_name}**"
        if team_name == "Team 7":
            response += " - BOMBERSSSSS 💣 💥"
        response += "\n"
        
        # Group members by role
        tanks = []
        healers = []
        dps = []
        
        for member in members:
            if member["role"] == "Tank":
                tanks.append(member["name"])
            elif member["role"] == "Healer":
                healers.append(member["name"])
            elif member["role"] == "Damage Dealer":
                dps.append(member["name"])
        
        # Add roles to response
        if tanks:
            response += f"Tank: {', '.join(tanks)}\n"
        if healers:
            response += f"Healer: {', '.join(healers)}\n"
        if dps:
            response += f"DPS: {', '.join(dps)}\n"
        
        response += "\n"  # Add spacing between teams

    # Add Fillers section at the end
    if "Fillers" in teams_data:
        response += "**Available Fillers:**\n"
        
        # Group fillers by role
        filler_tanks = []
        filler_healers = []
        filler_dps = []
        
        for member in teams_data["Fillers"]:
            if member["role"] == "Tank":
                filler_tanks.append(member["name"])
            elif member["role"] == "Healer":
                filler_healers.append(member["name"])
            elif member["role"] == "Damage Dealer":
                filler_dps.append(member["name"])
        
        # Add filler roles to response
        if filler_tanks:
            response += f"Tanks: {', '.join(filler_tanks)}\n"
        if filler_healers:
            response += f"Healers: {', '.join(filler_healers)}\n"
        if filler_dps:
            response += f"DPS: {', '.join(filler_dps)}\n"

    await ctx.send(response)

@bot.command(name="suggest")
async def suggest_teams(ctx):
    try:
        # Load teams data
        with open("teams.json", "r", encoding="utf-8") as file:
            teams_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("❌ Error loading teams data.")
        return

    # Get voice channel
    voice_channel = ctx.guild.get_channel(VOICE_CHANNEL_ID)
    if not voice_channel:
        await ctx.send("❌ Voice channel not found!")
        return

    # Get active members in voice channel
    active_members = [member.display_name for member in voice_channel.members]
    if not active_members:
        await ctx.send("❌ No members found in voice channel!")
        return

    response = "**Team Analysis and Suggestions:**\n\n"
    available_fillers = {
        "Tank": [],
        "Healer": [],
        "Damage Dealer": []
    }

    # Collect available fillers from voice channel
    for member in teams_data["Fillers"]:
        if member["name"] in active_members:
            available_fillers[member["role"]].append(member["name"])

    # Analyze each main team
    new_team_members = []  # Store leftover fillers for potential new team
    
    for team_name, team_members in teams_data.items():
        if team_name == "Fillers" or team_name == "Team 7":  # Skip Fillers and Team 7
            continue

        active_team_members = [m for m in team_members if m["name"] in active_members]
        
        # Count roles in active team members
        role_count = {
            "Tank": sum(1 for m in active_team_members if m["role"] == "Tank"),
            "Healer": sum(1 for m in active_team_members if m["role"] == "Healer"),
            "Damage Dealer": sum(1 for m in active_team_members if m["role"] == "Damage Dealer")
        }

        # Check if team needs members
        if len(active_team_members) < 6:
            response += f"**{team_name}** needs:\n"
            
            # Check missing roles
            if role_count["Tank"] < 1:
                response += f"- Tank (Suggestions: {', '.join(available_fillers['Tank']) or 'None'})\n"
            if role_count["Healer"] < 1:
                response += f"- Healer (Suggestions: {', '.join(available_fillers['Healer']) or 'None'})\n"
            if role_count["Damage Dealer"] < 4:
                needed_dps = 4 - role_count["Damage Dealer"]
                response += f"- {needed_dps} DPS (Suggestions: {', '.join(available_fillers['Damage Dealer'][:needed_dps]) or 'None'})\n"
            
            response += "\n"

    # Check if we can form a new team from remaining fillers
    remaining_fillers = {
        "Tank": [m for m in available_fillers["Tank"] if m not in new_team_members],
        "Healer": [m for m in available_fillers["Healer"] if m not in new_team_members],
        "Damage Dealer": [m for m in available_fillers["Damage Dealer"] if m not in new_team_members]
    }

    if (len(remaining_fillers["Tank"]) >= 1 and 
        len(remaining_fillers["Healer"]) >= 1 and 
        len(remaining_fillers["Damage Dealer"]) >= 4):
        
        response += "**Possible New Team from Remaining Fillers:**\n"
        response += f"Tank: {remaining_fillers['Tank'][0]}\n"
        response += f"Healer: {remaining_fillers['Healer'][0]}\n"
        response += f"DPS: {', '.join(remaining_fillers['Damage Dealer'][:4])}\n"

    if response == "**Team Analysis and Suggestions:**\n\n":
        response += "All teams are properly filled! ✅"

    await ctx.send(response)
    
# Run the bot
bot.run(TOKEN)
