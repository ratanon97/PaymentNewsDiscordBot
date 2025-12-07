# Payment News Discord Bot

A Discord bot that aggregates payment industry news from RSS feeds, uses AI to summarize and categorize articles, and delivers daily digests.

## Features

- Fetches news from The Paypers and Finextra RSS feeds
- AI-powered article summarization using Anthropic's Claude
- Automatic categorization (Global vs Thailand-specific)
- Daily scheduled digests at 8 AM Bangkok time
- Manual commands for on-demand news
- SQLite database to prevent duplicate articles

## Project Structure

```
PaymentNewsBot/
├── bot.py              # Discord bot logic and commands
├── news_fetcher.py     # RSS fetching and AI processing
├── database.py         # SQLite database operations
├── scheduler.py        # Daily digest scheduling
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── .env.example       # Environment variables template
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Enable "Message Content Intent" under Privileged Gateway Intents
5. Copy the bot token

### 3. Get Bot's Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click the channel where you want the bot to post
3. Click "Copy ID"

### 4. Get Anthropic API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create an API key

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 6. Invite Bot to Your Server

1. Go to Discord Developer Portal > Your Application > OAuth2 > URL Generator
2. Select scopes: `bot`
3. Select bot permissions: `Send Messages`, `Read Message History`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

## Usage

### Run Without Scheduler (Manual Commands Only)

```bash
python bot.py
```

### Run With Daily Scheduler

```bash
python scheduler.py
```

### Discord Commands

- `!digest` - Manually trigger a news digest (fetches new articles and displays them)
- `!latest` - Show the last 5 articles from the database

## Railway Deployment (24/7 Cloud Hosting)

To run your bot 24/7 in the cloud using Railway:

### 1. Push to GitHub

```bash
# Create a new repository on GitHub (via web interface)
# Then connect your local repo:

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway

1. Go to [Railway](https://railway.app/) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your PaymentNewsBot repository
4. Railway will automatically detect your `Procfile` and `runtime.txt`

### 3. Configure Environment Variables

In your Railway project dashboard:

1. Go to "Variables" tab
2. Add these environment variables:
   - `DISCORD_TOKEN` = your_discord_bot_token
   - `DISCORD_CHANNEL_ID` = your_channel_id
   - `ANTHROPIC_API_KEY` = your_anthropic_api_key

### 4. Deploy

Railway will automatically deploy your bot. Check the deployment logs to ensure it started successfully.

### Important Notes for Railway

- Railway uses the `Procfile` to know how to run your app
- The bot runs as a "worker" process (not a web server)
- The database file will persist across deployments
- Check logs via Railway dashboard if you encounter issues
- The bot will restart automatically if it crashes

### Railway Costs

Railway offers:
- $5 free credit per month (sufficient for a small Discord bot)
- Pay-as-you-go pricing after free credits
- This bot typically uses minimal resources (~$5-10/month)

## Configuration

Edit `config.py` to customize:

- RSS feed sources
- Digest time (default: 08:00 Bangkok time)
- Number of articles shown in `!latest` command
- Command prefix (default: `!`)

## Database

The bot uses SQLite to store articles and prevent duplicates. The database file `payment_news.db` is created automatically on first run.

## How It Works

1. **Fetching**: Bot fetches articles from configured RSS feeds
2. **Processing**: Each article is sent to Claude API for:
   - 2-3 sentence summary
   - Categorization (Global or Thailand-specific)
3. **Storage**: Articles are stored in SQLite with deduplication
4. **Delivery**: Articles are formatted and sent to Discord channel
5. **Scheduling**: Daily digest runs automatically at 8 AM Bangkok time

## Next Steps

After the basic bot is working, you can add:
- Reaction-based article saving
- User preferences for categories
- Web scraping for non-RSS sources
- Article search functionality
- Analytics and trending topics

## Troubleshooting

**Bot doesn't respond to commands:**
- Ensure "Message Content Intent" is enabled in Discord Developer Portal
- Check that the bot has permission to read/send messages in the channel

**API errors:**
- Verify your Anthropic API key is valid and has credits
- Check your Discord token is correct

**No articles showing:**
- RSS feeds may be down or changed URLs
- Check console for error messages
- Try running `!digest` manually to see detailed errors
