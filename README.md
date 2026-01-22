# DiscordCanvas

A Discord bot that integrates with Canvas to provide announcements directly in your Discord server.

## Acknowledgements

This project is inspired by and builds upon the work of Edvard Pedersen's [CanvasHelper](https://github.com/EdvardPedersen/CanvasHelper).

## Project Structure

```text
DiscordCanvas/
├── src/
│   ├── bot.py                  # Main Discord bot entry point
│   ├── canvas_integration.py   # Canvas API integration logic
│   ├── config.py               # Configuration and settings
│   ├── .env                    # Environment variables (create this)
│   └── .env.example            # Example environment configuration
│
├── .dockerignore            # Docker ignore file
├── .gitignore               # Git ignore file
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
├── cspell.json              # Spell checker configuration
├── project-words.txt        # Custom dictionary
└── README.md                # Project documentation
```

## Getting started

### Prerequisites

To run this project, you need to get key credentials from both Discord and Canvas:

1. **Discord Bot Token**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Create a new application and add a bot to it.
   - Copy the bot token from the "Bot" section.

2. **Canvas API Key**:
   - Log in to your Canvas account.
   - Navigate to "Konto" > "Innstillinger".
   - Scroll down to "Godkjente integrasjoner" and click on "New Access Token".

#### Discord Bot Permissions

When setting up your Discord bot, ensure it has the following permissions:

- Read Messages
- Send Messages
- Embed Links
- Read Message History
- Mention Everyone

### Local Setup

To get started with this project, follow these steps:

1. Set up a Python environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

2. **Set up `.env` file**: Create a `.env` file in the `src/` directory with the following content:

   ```env
   DISCORD_TOKEN=your_discord_bot_token
   CANVAS_TOKEN=your_canvas_api_token
   ```

   See `src/.env.example` for reference.

### Docker Setup

```bash
# Build and run with docker-compose
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop
docker-compose down
```

## Running the Code

**Locally:**

```bash
python src/bot.py
```

**With Docker:**

```bash
docker-compose up
```

## Building and Deploying Docker Image

```bash
# Build the Docker image
docker build -t discord-canvas-bot .

# You can run the image locally to test
docker run --rm --env-file src/.env discord-canvas-bot

# Tag the image for your Docker registry (replace YOUR_USERNAME)
docker tag discord-canvas-bot YOUR_USERNAME/discord-canvas-bot:latest

# Push the image to Docker Hub
docker push YOUR_USERNAME/discord-canvas-bot:latest
```
