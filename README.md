# TTM Discord Bot

## This bot was originally made for Trauma420 (Throne and Liberty)

## Overview
TTM is a Discord bot designed to assist with team management, event scheduling, attendance tracking, and VOD submissions for a gaming community. It integrates with the Groq API for event extraction and provides various administrative and user commands.

## Features
- **Team Management:** View team assignments, roles, and available fillers.
- **Event Scheduling:** Automatically extract events from messages and maintain a schedule.
- **Attendance Tracking:** Record attendance from voice channels and provide statistics.
- **VOD Management:** Submit and retrieve VOD links for review.
- **Admin Controls:** Manage events, attendance, and team assignments with admin commands.

## Requirements
- Python 3.8+
- Discord API
- Groq API
- Required Python Libraries:
  - `discord.py`
  - `json`
  - `pytz`
  - `re`
  - `os`
  - `datetime`

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/marawan206/TLDiscord_Bot
   cd TTM
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the bot:
   - Set your **Discord Bot Token** and **Groq API Key** in `TTM.py`
   - Specify **Role IDs, Channel IDs, and User IDs** where needed.
4. Run the bot:
   ```bash
   python TTM.py
   ```

## Usage
### General Commands
- `!commands` - Show available commands.
- `!whois <username>` - Display a user’s role and team.
- `!myteam` - View your assigned team members.
- `!myatt` - Check your attendance statistics.
- `!today` - Display today’s scheduled events.
- `!allteams` - List all teams and their members.
- `!suggest` - Suggest team fillers based on voice channel activity.

### Admin Commands
- `!attendance <event_name>` - Record attendance from the voice channel.
- `!add <name> <time> [description]` - Add an event to the schedule.
- `!details <username>` - Show detailed attendance for a user.

### VOD Commands
- `!vodlink <vod_name> <link>` - Submit a VOD link.
- `!listvods` - List all available VODs and their submission counts.
- `!addvod <vod_name>` - Add a new VOD category (Admin only).
- `!vodinfo <vod_name>` - Display all submissions for a VOD (Admin only).

## Configuration
The bot requires manual configuration in `TTM.py`. Update the following placeholders:
- `TOKEN = "your-discord-bot-token"`
- `GROQ_API_KEY = "your-groq-api-key"`
- Replace `<SPECIFY IF NEEDED>` with actual Role IDs, Channel IDs, and User IDs.

## File Structure
- `TTM.py` - The main bot script.
- `teams.json` - Stores team assignments and roles.
- `attendance.json` - Tracks attendance records.
- `schedule.json` - Maintains scheduled events.
- `vods.json` - Stores VOD submissions and categories.

## Contributing
Pull requests are welcome. Please ensure that your contributions align with the existing coding style and functionality.

## License
This project is licensed under the MIT License.

## Contact
For questions or issues, contact the project maintainers on Discord.

