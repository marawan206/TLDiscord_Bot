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
        await show_todays_events(interaction)
    elif interaction.data["custom_id"] == "my_team":
        await interaction.response.send_message("Fetching your team info...", ephemeral=True)
        await show_my_team(interaction)
    elif interaction.data["custom_id"] == "attendance":
        await interaction.response.send_message("Checking attendance...", ephemeral=True)
        await check_attendance(interaction)
    elif interaction.data["custom_id"] == "vods":
        await interaction.response.send_message("Listing VODs...", ephemeral=True)
        await list_vods(interaction)

# Show Today's Events
async def show_todays_events(interaction: discord.Interaction):
    try:
        with open("schedule.json", "r") as file:
            schedule = json.load(file)
        today_date = datetime.now(pytz.timezone("CET")).strftime("%Y-%m-%d")
        if today_date not in schedule:
            await interaction.response.send_message("No events scheduled for today.", ephemeral=True)
            return
        response = "**Today's Events (CET):**\n"
        for event in schedule[today_date]:
            response += f"- **{event['name']}**: {event['time']} | {event['description']}\n"
        await interaction.response.send_message(response, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error fetching today's events: {e}", ephemeral=True)

# Show My Team
async def show_my_team(interaction: discord.Interaction):
    user_name = interaction.user.display_name
    user_team = next((team for team, members in teams.items() if any(m["name"].lower() == user_name.lower() for m in members)), None)
    if not user_team:
        await interaction.response.send_message("You are not assigned to any team.", ephemeral=True)
        return
    team_members = [m["name"] for m in teams[user_team]]
    response = f"**Your Team:** {user_team}\n**Members:** {', '.join(team_members)}"
    await interaction.response.send_message(response, ephemeral=True)

# Check Attendance
async def check_attendance(interaction: discord.Interaction):
    user_name = interaction.user.display_name
    attended_events = [
        f"{event['name']} at {event['time']}"
        for day, events in attendance_data.items()
        for event in events.values()
        if user_name in event["attendees"]
    ]
    if not attended_events:
        await interaction.response.send_message("You have no attendance records.", ephemeral=True)
    else:
        response = "**Your Attendance Record:**\n" + "\n".join(attended_events)
        await interaction.response.send_message(response, ephemeral=True)
class VODMenu(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Submit VOD", style=discord.ButtonStyle.primary, custom_id="submit_vod"))
        self.add_item(Button(label="List VODs", style=discord.ButtonStyle.secondary, custom_id="list_vods"))
        self.add_item(Button(label="VOD Info", style=discord.ButtonStyle.success, custom_id="vod_info"))

@bot.command(name="vodmenu")
async def show_vod_menu(ctx):
    view = VODMenu()
    await ctx.send("Manage VODs using the buttons below:", view=view)
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "submit_vod":
        await interaction.response.send_message("Please enter the VOD name and link in the format: `vod_name, link`", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_name, vod_link = msg.content.split(", ", 1)
            save_vod_submission(vod_name, vod_link, interaction.user.display_name)
            await interaction.followup.send(f"✅ VOD `{vod_name}` submitted successfully!", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Invalid format. Use `vod_name, link`", ephemeral=True)

    elif interaction.data["custom_id"] == "list_vods":
        vod_list = load_vod_list()
        await interaction.response.send_message(f"📜 **Available VODs:**\n{vod_list}", ephemeral=True)

    elif interaction.data["custom_id"] == "vod_info":
        await interaction.response.send_message("Enter the VOD name:", ephemeral=True)

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_info = get_vod_info(msg.content)
            await interaction.followup.send(vod_info, ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ VOD not found.", ephemeral=True)
# Load VOD data
def load_vod_data():
    try:
        with open("vods.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"vod_names": [], "vod_links": {}}

# Save VOD data
def save_vod_data(data):
    with open("vods.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Handle VOD Button Interactions
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "submit_vod":
        await interaction.response.send_message("Please enter the VOD name and link in the format: `vod_name, link`", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_name, vod_link = msg.content.split(", ", 1)
            
            vod_data = load_vod_data()
            if vod_name not in vod_data["vod_links"]:
                vod_data["vod_links"][vod_name] = {}
            vod_data["vod_links"][vod_name][interaction.user.display_name] = vod_link
            save_vod_data(vod_data)

            await interaction.followup.send(f"✅ VOD `{vod_name}` submitted successfully!", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Invalid format. Use `vod_name, link`", ephemeral=True)

    elif interaction.data["custom_id"] == "list_vods":
        vod_data = load_vod_data()
        if not vod_data["vod_names"]:
            await interaction.response.send_message("No VODs available.", ephemeral=True)
            return
        
        response = "**Available VODs:**\n" + "\n".join(vod_data["vod_names"])
        await interaction.response.send_message(response, ephemeral=True)

    elif interaction.data["custom_id"] == "vod_info":
        await interaction.response.send_message("Enter the VOD name to view details:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_name = msg.content

            vod_data = load_vod_data()
            if vod_name not in vod_data["vod_links"]:
                await interaction.followup.send("❌ VOD not found.", ephemeral=True)
                return

            vod_links = vod_data["vod_links"][vod_name]
            response = f"**VOD Links for {vod_name}:**\n" + "\n".join([f"{user}: {link}" for user, link in vod_links.items()])
            await interaction.followup.send(response, ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Invalid input.", ephemeral=True)
# Load VOD data
def load_vod_data():
    try:
        with open("vods.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"vod_names": [], "vod_links": {}}

# Save VOD data
def save_vod_data(data):
    with open("vods.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Handle VOD Button Interactions
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "submit_vod":
        await interaction.response.send_message("Please enter the VOD name and link in the format: `vod_name, link`", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_name, vod_link = msg.content.split(", ", 1)
            
            vod_data = load_vod_data()
            if vod_name not in vod_data["vod_links"]:
                vod_data["vod_links"][vod_name] = {}
            vod_data["vod_links"][vod_name][interaction.user.display_name] = vod_link
            save_vod_data(vod_data)

            await interaction.followup.send(f"✅ VOD `{vod_name}` submitted successfully!", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Invalid format. Use `vod_name, link`", ephemeral=True)

    elif interaction.data["custom_id"] == "list_vods":
        vod_data = load_vod_data()
        if not vod_data["vod_names"]:
            await interaction.response.send_message("No VODs available.", ephemeral=True)
            return
        
        response = "**Available VODs:**\n" + "\n".join(vod_data["vod_names"])
        await interaction.response.send_message(response, ephemeral=True)

    elif interaction.data["custom_id"] == "vod_info":
        await interaction.response.send_message("Enter the VOD name to view details:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
            vod_name = msg.content

            vod_data = load_vod_data()
            if vod_name not in vod_data["vod_links"]:
                await interaction.followup.send("❌ VOD not found.", ephemeral=True)
                return

            vod_links = vod_data["vod_links"][vod_name]
            response = f"**VOD Links for {vod_name}:**\n" + "\n".join([f"{user}: {link}" for user, link in vod_links.items()])
            await interaction.followup.send(response, ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Invalid input.", ephemeral=True)
bot.run(TOKEN)
