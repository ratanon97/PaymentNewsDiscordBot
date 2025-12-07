"""
Discord Bot Module

This module implements the Discord bot with command handlers for news digest functionality.
Handles user commands and scheduled digest delivery.

Requirements:
- TR-004: Discord Integration
- TR-021: Command - !digest
- TR-022: Command - !latest
- TR-023: Message Length Handling
- TR-025: Scheduled Digest Process
- TR-029: Console Logging
- TR-030: Exception Handling
- TR-031: Discord API Error Handling
"""

import discord
from discord.ext import commands
import logging
import asyncio
import config
from news_fetcher import NewsFetcher, NewsFetcherError
from database import NewsDatabase, DatabaseError

# Configure logging - TR-029: Console Logging
logger = logging.getLogger(__name__)

# TR-004: Set up Discord intents (requires Message Content Intent)
intents = discord.Intents.default()
intents.message_content = True  # TR-004: Required for reading message content

# TR-004: Create bot instance with configured prefix
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# Initialize services with error handling
try:
    news_fetcher = NewsFetcher()
    db = NewsDatabase()
    logger.info("Bot services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot services: {e}")
    raise


@bot.event
async def on_ready():
    """
    Event handler for when the bot is ready

    Requirements:
    - TR-029: Console Logging
    - TR-004: Discord connection status
    """
    # TR-029: Log connection status
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')

    # Log configuration status
    config.log_configuration_status()


@bot.event
async def on_command_error(ctx, error):
    """
    Global error handler for bot commands

    Requirements:
    - TR-030: Exception Handling
    - TR-031: Discord API Error Handling
    """
    if isinstance(error, commands.CommandNotFound):
        logger.debug(f"Unknown command attempted: {ctx.message.content}")
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
        return

    if isinstance(error, discord.errors.Forbidden):
        # TR-031: Handle insufficient permissions
        logger.error(f"Missing permissions in channel {ctx.channel.id}: {error}")
        await ctx.send("❌ I don't have permission to perform this action.")
        return

    # Log unexpected errors
    logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
    await ctx.send(f"❌ An unexpected error occurred. Please try again later.")


@bot.command(name='digest')
async def digest(ctx):
    """
    Manually trigger a news digest

    Requirements:
    - TR-021: Command - !digest implementation
    - TR-023: Message Length Handling
    - TR-030: Exception Handling

    Args:
        ctx: Discord command context
    """
    # TR-021: Send acknowledgment message
    logger.info(f"Digest command triggered by {ctx.author} in {ctx.channel}")
    await ctx.send("Fetching and processing latest news... This may take a moment.")

    try:
        # TR-021: Fetch and process new articles
        logger.info("Starting fetch and process operation")
        new_articles_count = news_fetcher.fetch_and_process_news()
        logger.info(f"Processed {new_articles_count} new articles")

        # TR-021: Get unsent articles from database
        articles = db.get_unsent_articles()

        if not articles:
            # TR-021: Handle no articles case
            await ctx.send("No new articles to report.")
            logger.info("No new articles to send in digest")
            return

        # TR-021: Create formatted digest with embeds
        digest_data = news_fetcher.create_digest(articles)

        # Send header
        await ctx.send(digest_data['header'])

        # TR-028: Send Thailand-specific section
        if digest_data['thailand_embeds']:
            await ctx.send("## 🇹🇭 THAILAND-SPECIFIC NEWS")
            for embed in digest_data['thailand_embeds']:
                msg = await ctx.send(embed=embed)
                # Add emoji reactions
                await msg.add_reaction("📌")  # Pin/save
                await msg.add_reaction("💬")  # Comment/discuss
                await msg.add_reaction("🔗")  # Share
                await asyncio.sleep(0.3)  # Avoid rate limiting

        # TR-028: Send Global section
        if digest_data['global_embeds']:
            await ctx.send("## 🌏 GLOBAL NEWS")
            for embed in digest_data['global_embeds']:
                msg = await ctx.send(embed=embed)
                # Add emoji reactions
                await msg.add_reaction("📌")  # Pin/save
                await msg.add_reaction("💬")  # Comment/discuss
                await msg.add_reaction("🔗")  # Share
                await asyncio.sleep(0.3)  # Avoid rate limiting

        # TR-021: Mark articles as sent
        article_ids = [a['id'] for a in articles]
        db.mark_articles_sent(article_ids)

        # TR-021: Send completion message
        await ctx.send(f"✅ Digest complete! Processed {new_articles_count} new articles.")
        logger.info(f"Digest command completed successfully: {len(articles)} articles sent")

    except NewsFetcherError as e:
        # TR-030: Handle news fetcher specific errors
        error_msg = f"❌ Error fetching news: {str(e)}"
        await ctx.send(error_msg)
        logger.error(f"NewsFetcherError in digest command: {e}")

    except DatabaseError as e:
        # TR-030: Handle database specific errors
        error_msg = f"❌ Database error: {str(e)}"
        await ctx.send(error_msg)
        logger.error(f"DatabaseError in digest command: {e}")

    except discord.errors.HTTPException as e:
        # TR-031: Handle Discord API errors
        logger.error(f"Discord HTTP error in digest command: {e}")
        await ctx.send("❌ Error communicating with Discord. Please try again.")

    except Exception as e:
        # TR-030: Handle unexpected errors
        error_msg = f"❌ Unexpected error: {str(e)}"
        await ctx.send(error_msg)
        logger.error(f"Unexpected error in digest command: {e}", exc_info=True)


@bot.command(name='latest')
async def latest(ctx):
    """
    Show the last N articles from the database

    Requirements:
    - TR-022: Command - !latest implementation
    - TR-023: Message Length Handling
    - TR-030: Exception Handling

    Args:
        ctx: Discord command context
    """
    logger.info(f"Latest command triggered by {ctx.author} in {ctx.channel}")

    try:
        # TR-022: Get latest articles from database
        articles = db.get_latest_articles(limit=config.MAX_ARTICLES_LATEST)

        if not articles:
            # TR-022: Handle empty database case
            await ctx.send("No articles found in the database.")
            logger.info("No articles in database for latest command")
            return

        # TR-022: Send response header
        await ctx.send(f"**📰 Latest {len(articles)} Articles**\n")

        # TR-022: Send each article as an embed
        for article in articles:
            embed = news_fetcher.format_article_for_discord(article)
            msg = await ctx.send(embed=embed)

            # Add emoji reactions
            await msg.add_reaction("📌")  # Pin/save
            await msg.add_reaction("💬")  # Comment/discuss
            await msg.add_reaction("🔗")  # Share
            await asyncio.sleep(0.3)  # Avoid rate limiting

        logger.info(f"Latest command completed: {len(articles)} articles shown")

    except DatabaseError as e:
        # TR-030: Handle database specific errors
        error_msg = f"❌ Database error: {str(e)}"
        await ctx.send(error_msg)
        logger.error(f"DatabaseError in latest command: {e}")

    except discord.errors.HTTPException as e:
        # TR-031: Handle Discord API errors
        logger.error(f"Discord HTTP error in latest command: {e}")
        await ctx.send("❌ Error communicating with Discord. Please try again.")

    except Exception as e:
        # TR-030: Handle unexpected errors
        error_msg = f"❌ Unexpected error: {str(e)}"
        await ctx.send(error_msg)
        logger.error(f"Unexpected error in latest command: {e}", exc_info=True)


def split_message(text: str, max_length: int = 2000) -> list:
    """
    Split a long message into chunks that fit Discord's character limit

    Requirements:
    - TR-023: Message Length Handling
    - TR-033: Input Validation

    Args:
        text: Message text to split
        max_length: Maximum length per chunk (default: 2000)

    Returns:
        List of message chunks
    """
    # TR-033: Validate inputs
    if not text:
        return [""]

    if not isinstance(max_length, int) or max_length <= 0:
        logger.warning(f"Invalid max_length {max_length}, using default 2000")
        max_length = 2000

    chunks = []
    current_chunk = ""

    # TR-023: Split by newlines to preserve formatting
    lines = text.split('\n')

    for line in lines:
        # If a single line exceeds max_length, split it
        if len(line) > max_length:
            logger.warning(f"Single line exceeds max_length, truncating: {line[:50]}...")
            line = line[:max_length - 3] + "..."

        # Check if adding this line would exceed limit
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += '\n' + line
            else:
                current_chunk = line

    # Add remaining content
    if current_chunk:
        chunks.append(current_chunk)

    logger.debug(f"Split message into {len(chunks)} chunks")
    return chunks


async def send_scheduled_digest():
    """
    Send scheduled digest to the configured channel

    Requirements:
    - TR-025: Scheduled Digest Process
    - TR-023: Message Length Handling
    - TR-029: Console Logging
    - TR-030: Exception Handling

    This function is called by the scheduler module.
    """
    logger.info("Starting scheduled digest")

    try:
        # TR-025: Fetch and process new articles
        logger.info("Fetching and processing articles for scheduled digest")
        new_articles_count = news_fetcher.fetch_and_process_news()
        logger.info(f"Processed {new_articles_count} new articles for scheduled digest")

        # TR-025: Get unsent articles
        articles = db.get_unsent_articles()

        if not articles:
            # TR-025: Log and exit if no articles
            logger.info("No new articles for scheduled digest")
            return

        # TR-025: Get the configured channel
        channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
        if not channel:
            # TR-025: Log error if channel not found
            logger.error(f"Channel {config.DISCORD_CHANNEL_ID} not found")
            return

        # TR-025: Create digest with embeds
        digest_data = news_fetcher.create_digest(articles)

        # Send header
        await channel.send(digest_data['header'])

        # TR-028: Send Thailand-specific section
        if digest_data['thailand_embeds']:
            await channel.send("## 🇹🇭 THAILAND-SPECIFIC NEWS")
            for embed in digest_data['thailand_embeds']:
                msg = await channel.send(embed=embed)
                # Add emoji reactions
                await msg.add_reaction("📌")  # Pin/save
                await msg.add_reaction("💬")  # Comment/discuss
                await msg.add_reaction("🔗")  # Share
                await asyncio.sleep(0.3)  # Avoid rate limiting

        # TR-028: Send Global section
        if digest_data['global_embeds']:
            await channel.send("## 🌏 GLOBAL NEWS")
            for embed in digest_data['global_embeds']:
                msg = await channel.send(embed=embed)
                # Add emoji reactions
                await msg.add_reaction("📌")  # Pin/save
                await msg.add_reaction("💬")  # Comment/discuss
                await msg.add_reaction("🔗")  # Share
                await asyncio.sleep(0.3)  # Avoid rate limiting

        # TR-025: Mark articles as sent
        article_ids = [a['id'] for a in articles]
        db.mark_articles_sent(article_ids)

        # TR-029: Log success
        logger.info(f"Scheduled digest sent! Processed {new_articles_count} new articles, sent {len(articles)} articles")

    except NewsFetcherError as e:
        logger.error(f"NewsFetcherError in scheduled digest: {e}")

    except DatabaseError as e:
        logger.error(f"DatabaseError in scheduled digest: {e}")

    except discord.errors.HTTPException as e:
        # TR-031: Handle Discord API errors
        logger.error(f"Discord HTTP error in scheduled digest: {e}")

    except Exception as e:
        # TR-030: Handle unexpected errors
        logger.error(f"Unexpected error in scheduled digest: {e}", exc_info=True)


def run_bot():
    """
    Run the Discord bot

    Requirements:
    - TR-004: Discord Integration
    - TR-032: Credential Management
    - TR-033: Input Validation

    Validates configuration and starts the bot.
    """
    # TR-033: Validate Discord token
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error("Please configure DISCORD_TOKEN in .env file")
        return

    # TR-033: Validate configuration
    try:
        config.validate_configuration()
    except config.ConfigurationError as e:
        logger.error(f"Configuration validation failed: {e}")
        return

    try:
        # TR-004: Run bot with token
        logger.info("Starting Discord bot...")
        bot.run(config.DISCORD_TOKEN, log_handler=None)  # Use our custom logging
    except discord.errors.LoginFailure:
        logger.error("Invalid Discord token. Please check your DISCORD_TOKEN in .env file")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)


if __name__ == '__main__':
    run_bot()
