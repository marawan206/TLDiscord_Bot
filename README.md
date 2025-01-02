# Throne and Liberty Discord Bot

A comprehensive Discord bot for managing Throne and Liberty (TL) gaming community, featuring enhanced attendance tracking, event management, and team organization capabilities.

## Features

### Event Management
- **Automatic Event Detection**
  - Monitors specific channels for event announcements
  - Uses Groq AI to extract event details automatically
  - Supports manual event addition by administrators

### Attendance System
- **Advanced Attendance Tracking**
  - Automatic voice channel attendance monitoring
  - Persistent attendance records stored in JSON format
  - Historical attendance data tracking
  - Team completion status checking

### Team Management
- **Comprehensive Team Organization**
  - Role-based team structure (Healers, Damage Dealers, Tanks)
  - Team composition tracking
  - Special team designations (e.g., "Bombers" team)
  - Individual team member status

### User Information
- **Detailed Member Tracking**
  - Role and team lookup
  - Special user recognitions
  - Team assignment verification
  - Current status checking

## Prerequisites

- Python 3.8+
- Required Python packages:
  ```
  discord.py
  pytz
  groq
  ```
- Discord Bot Token
- Groq API Key

## Configuration Files

### config.json
```json
{
    "TOKEN": "your-discord-bot-token",
    "GROQ_API_KEY": "your-groq-api-key",
    "CHANNEL_IDS": {
        "TEXT": "your-text-channel-id",
        "VOICE": "your-voice-channel-id",
        "WATCHED": "your-watched-channel-id"
    },
    "ROLE_IDS": {
        "ADMIN": "your-admin-role-id",
        "HIGHER_ADMIN": "your-higher-admin-role-id",
        "MEMBER": "your-member-role-id"
    }
}
```

### teams.json
```json
{
    "Team1": [
        {"name": "Player1", "role": "Healer"},
        {"name": "Player2", "role": "Tank"}
    ],
    "Bombers": [
        {"name": "Player3", "role": "Damage Dealer"},
        {"name": "Player4", "role": "Healer"}
    ]
}
```

## Commands

### General Commands
- `!commands` - Display all available commands
- `!today` - Show today's scheduled events
- `!whois <username>` - Look up user information

### Team Commands
- `!myteam` - View your team's information and members

### Admin Commands
- `!attendance` - Record and display attendance (Admin only)
- `!add <name> <time> [description]` - Add new events (Admin only)

## File Structure
```
├── bot.py
├── config.json
├── teams.json
├── schedule.json
├── attendance.json
└── README.md
```

## New Features and Updates

### Attendance System
- Enhanced attendance tracking with persistent storage
- Historical attendance records
- Automatic voice channel monitoring
- Team completion checking

### Event Management
- AI-powered event extraction using Groq
- Automatic event scheduling from announcements
- Manual event addition capability

### Special Features
- Special recognition for specific users/roles
- Team-specific messages (e.g., Bomber Group designation)
- Timezone support (CET)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration files:
   - Create `config.json` with your credentials
   - Set up `teams.json` with your team structure
   - Ensure proper permissions for JSON files

4. Run the bot:
```bash
python bot.py
```

## Security Notes

- Store sensitive credentials in config.json (not in code)
- Implement proper role-based access control
- Regular credential rotation
- Backup attendance and schedule data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support, please:
1. Check the existing documentation
2. Contact server administrators
3. Create an issue in the repository