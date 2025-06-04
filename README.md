# Discord Bot with Gemini AI

A Discord bot that uses Google's Gemini AI to provide chat functionality and image generation with customizable response tones.

## Features

- **Chat functionality**: Responds when mentioned (@bot) and maintains conversation context
- **Customizable Tone System**: 5 different response tones from very flattery to noble
- **Slash commands**: Modern Discord commands with "/" prefix
- **Command-based interaction**: Traditional commands with the "!" prefix
- **Image generation**: Create images from text descriptions
- **Context management**: Maintains separate conversation history for each user
- **Chat summarization**: Summarize recent chat messages in channels

## Tone System

The bot supports 5 distinct tone levels that can be configured per server:
| Level | Name | Description |
|-------|------|-------------|
| 1 | Very Flattery | Extremely flattering, excessive praise, user idolization |
| 2 | Flattery | Gentle flattery, positive but still professional |
| 3 | Neuter (Default) | Neutral, professional, emotionless |
| 4 | Elegant | Courteous, refined, subtle and attentive |
| 5 | Noble | Noble, philosophical, formal and erudite |

### Tone Configuration Commands

- `/tone` - Configure tone with dropdown UI (requires Manage Server permission)
- `!tone [1-5]` - Set tone level directly (requires Manage Server permission)
- `!tone` - Show current tone and available options
- `/tone_demo` - Demonstrate all tone responses with sample input

## Commands

### Chat Commands
- Mention the bot: `@BotName How are you today?`
- `/chat [message]` - Chat with the AI using slash command
- `/clear_context` or `!clear_context` - Reset chat history

### Image Generation
- `/imagine [prompt]` - Generate images from text descriptions
- `!imagine [description]` - Generate images using prefix command

### Utility Commands
- `/summary [count]` - Summarize recent chat messages (default: 10)
- `!summary [count]` - Summarize using prefix command
- `/tone` - Configure bot response tone for the server
- `/tone_demo` - See examples of all tone levels

## Local Setup

1. Clone this repository
2. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run the bot: `python main.py`

## Deploying to AWS EC2

This project uses GitHub Actions for automated deployment to AWS EC2.

### Prerequisites

1. An AWS EC2 instance
2. The following GitHub secrets configured in your repository:
   - `EC2_SSH_KEY`: Private SSH key for connecting to your EC2 instance
   - `EC2_USER`: Username for SSH connection (e.g., `ec2-user`)
   - `EC2_HOST`: Public IP or hostname of your EC2 instance
   - `DISCORD_TOKEN`: Your Discord bot token
   - `GEMINI_API_KEY`: Your Gemini API key

### Deployment Options

#### Option 1: Direct Python Deployment

Uses systemd to manage the bot process.

1. Push to the `main` branch to trigger deployment
2. GitHub Actions will:
   - Connect to your EC2 instance
   - Clone/pull the repository
   - Install dependencies
   - Create a systemd service
   - Start the bot

#### Option 2: Docker Deployment

Uses Docker to containerize the application.

1. Make sure Docker is installed on your EC2 instance
2. Push to the `main` branch to trigger deployment
3. GitHub Actions will:
   - Connect to your EC2 instance
   - Clone/pull the repository
   - Build a Docker image
   - Run the bot in a container

## Setup

1. **Requirements**

   Make sure you have Python 3.8+ installed.

2. **Install dependencies**

   ```bash
   pip install discord.py google-generativeai python-dotenv
   ```

3. **Set up tokens**

   Create a `.env` file in the project root with the following:

   ```
   DISCORD_TOKEN=your_discord_token_here
   GEMINI_API_KEY=your_gemini_api_key
   ```

   - Get a Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
   - Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)

4. **Configure Bot Permissions in Discord Developer Portal**

   In the Discord Developer Portal:
   
   a. Go to your application → Bot section
   
   b. Under "Privileged Gateway Intents", enable:
      - SERVER MEMBERS INTENT
      - MESSAGE CONTENT INTENT
      - PRESENCE INTENT
   
   c. Save changes

5. **Invite the bot to your server**

   When you start the bot, it will print an invite link in the console. Use that link to add the bot to your server.
   
   This link includes all the necessary permissions and scopes for the bot to:
   - Appear in the member list
   - Respond to mentions
   - Use slash commands

## Usage

1. **Start the bot**

   ```bash
   python main.py
   ```

2. **Chat with the bot**

   - Mention the bot: `@BotName How are you today?`
   - Use slash command: `/chat message:How are you today?`
   - The bot maintains conversation context, so it remembers previous messages.

3. **Configure Tone (Server Admins)**

   - Use `/tone` for dropdown selection
   - Use `!tone 3` to set directly to level 3 (Neuter)
   - Use `/tone_demo` to see examples of all tones

4. **Commands**

   **Slash Commands (recommended):**
   - `/chat [message]`: Chat with the AI
   - `/imagine [prompt]`: Generate an image from a description
   - `/clear_context`: Clear your conversation history
   - `/summary [count]`: Summarize recent messages
   - `/tone`: Configure bot tone (requires Manage Server)
   - `/tone_demo`: Demonstrate all tone levels

   **Traditional Commands:**
   - `!clear_context` (aliases: `!cc`, `!reset`): Clear your conversation history
   - `!imagine [description]` (aliases: `!img`, `!image`, `!create`): Generate an image from a description
   - `!summary [count]` (aliases: `!sum`, `!summarize`): Summarize recent messages
   - `!tone [1-5]`: Set tone level directly

## Troubleshooting

- **Bot not responding to mentions**: Make sure all privileged intents are enabled in the Discord Developer Portal.
- **Bot not showing in member list**: The bot needs the SERVER MEMBERS INTENT and PRESENCE INTENT enabled.
- **Commands not working**: Try re-inviting the bot using the automatically generated invite link from the console.
- **Tone not changing**: Make sure you have Manage Server permissions and try clearing context with `/clear_context`.

## Examples

- **Chat (mention)**: `@BotName What's the capital of France?`
- **Chat (slash command)**: `/chat message:What's the capital of France?`
- **Follow-up**: `@BotName And what's interesting to visit there?`
- **Generate image**: `/imagine prompt:a futuristic city with flying cars`
- **Reset conversation**: `/clear_context`
- **Configure tone**: `/tone` (then select from dropdown)
- **Set tone directly**: `!tone 4` (sets to Elegant tone)
- **See tone examples**: `/tone_demo`
