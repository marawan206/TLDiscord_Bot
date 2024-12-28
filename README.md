# Throne and Liberty Discord Bot

A Discord bot designed to manage teams, events, and attendance for the Throne and Liberty (TL) gaming community. The bot features team management, event scheduling, and attendance tracking capabilities.

## Features

- **Event Management**
  - Automatic event extraction from announcements
  - Manual event addition
  - Daily event schedule viewing
  
- **Team Management**
  - Team composition tracking
  - Role-based organization (Healers, Damage Dealers, Tanks)
  - Team member status checking
  
- **Attendance Tracking**
  - Real-time attendance monitoring
  - Role-based attendance summaries
  - Team completion status
  
- **User Information**
  - Player role lookup
  - Team assignment checking
  - Individual team status viewing

## Prerequisites

- Python 3.8+
- discord.py library
- Groq API access
- Discord Bot Token
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `config.json` file with your credentials:
```json
{
    "TOKEN": "your-discord-bot-token",
    "GROQ_API_KEY": "your-groq-api-key"
}
```

4. Create a `teams.json` file to define your teams structure:
```json
{
    "Team1": [
        {"name": "Player1", "role": "Healer"},
        {"name": "Player2", "role": "Tank"}
    ],
    "Team2": [
        {"name": "Player3", "role": "Damage Dealer"},
        {"name": "Player4", "role": "Healer"}
    ]
}
```

## Commands

- `!commands` - Display all available commands
- `!attendance` - Show attendance summary (Admin only)
- `!myteam` - Display your team's information
- `!add <name> <time> [description]` - Add a new event (Admin only)
- `!today` - Show today's scheduled events
- `!whois <username>` - Show role and team information for a user

## Configuration

Update the following constants in the code:
- `ADMIN_ROLE_ID` - Discord role ID for administrators
- `HIGHER_ADMIN_ROLE_ID` - Discord role ID for higher administrators
- `MEMBER_ROLE_ID` - Discord role ID for regular members
- `WATCHED_CHANNEL_ID` - Channel ID for event announcements
- `TEXT_CHANNEL_ID` - Main text channel ID
- `VOICE_CHANNEL_ID` - Voice channel ID for attendance tracking

## Running the Bot

```bash
python bot.py
```

## Security Notes

- Keep your Discord bot token and API keys secure
- Don't share your config.json file
- Regularly rotate security credentials
- Use role-based access control for administrative commands

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Support

For support, please join our Discord server or create an issue in the repository.