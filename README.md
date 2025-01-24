
# Tally

Discord bot for creating and managing counting channels.



## Features

- `/create-channel`: Creates a managed counting channel
- `/leaderboard`:  Displays a leaderboard for the top counters of your discord server
- `/current-number`:  Get the current number of a counting channel

## Setup

### Installation

Clone repository
```bash
git clone https://github.com/lenny015/tally.git
cd tally

```

Create virtual environment (recommended)

```bash
# Windows
python -m venv env
env/Scripts/activate
```

```bash
# macOS/Linux
source env/bin/activate
```

Rename `.envsample` to `.env`
```
BOT_TOKEN=INSERT_TOKEN_HERE
```

Starting the application
```
py src/bot.py
```



