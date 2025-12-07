"""
Scheduler Module

This module handles scheduled digest delivery at configured times.
Integrates with the Discord bot to send automated daily digests.

Requirements:
- TR-024: Scheduling Mechanism
- TR-025: Scheduled Digest Process
- TR-026: Timezone Handling
- TR-029: Console Logging
- TR-030: Exception Handling
"""

import asyncio
import schedule
import pytz
import logging
from datetime import datetime
import config
from bot import bot, send_scheduled_digest

# Configure logging - TR-029: Console Logging
logger = logging.getLogger(__name__)


class SchedulerError(Exception):
    """Raised when scheduler operations fail"""
    pass


class DigestScheduler:
    """
    Manages scheduled digest delivery

    Requirements:
    - TR-024: Scheduling Mechanism
    - TR-026: Timezone Handling
    """

    def __init__(self):
        """
        Initialize scheduler with configured timezone and digest time

        Requirements:
        - TR-026: Timezone Handling (pytz)
        """
        try:
            # TR-026: Set timezone
            self.timezone = pytz.timezone(config.TIMEZONE)
            self.digest_time = config.DIGEST_TIME

            logger.info(f"Scheduler initialized: {self.digest_time} {config.TIMEZONE}")

        except pytz.exceptions.UnknownTimeZoneError as e:
            logger.error(f"Invalid timezone '{config.TIMEZONE}': {e}")
            raise SchedulerError(f"Invalid timezone configuration: {e}")

        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise SchedulerError(f"Scheduler initialization failed: {e}")

    def schedule_digest(self):
        """
        Schedule the daily digest

        Requirements:
        - TR-024: Scheduling Mechanism
        - TR-029: Console Logging
        """
        try:
            # TR-024: Schedule task to run every day at configured time
            schedule.every().day.at(self.digest_time).do(self.run_async_digest)

            # TR-029: Log scheduling confirmation
            logger.info(f"Scheduled daily digest at {self.digest_time} {config.TIMEZONE}")

        except Exception as e:
            logger.error(f"Failed to schedule digest: {e}")
            raise SchedulerError(f"Scheduling failed: {e}")

    def run_async_digest(self):
        """
        Wrapper to run async digest function in bot's event loop

        Requirements:
        - TR-024: Execute async task in Discord bot event loop
        - TR-030: Exception Handling
        """
        try:
            # TR-024: Run coroutine in bot's event loop
            if bot.loop and not bot.loop.is_closed():
                asyncio.run_coroutine_threadsafe(send_scheduled_digest(), bot.loop)
                logger.debug("Scheduled digest task queued")
            else:
                logger.error("Bot event loop is not running or is closed")

        except Exception as e:
            logger.error(f"Error scheduling async digest: {e}")

    async def start_scheduler(self):
        """
        Start the scheduler loop

        Requirements:
        - TR-024: Check for pending tasks every 60 seconds
        - TR-030: Exception Handling

        This runs as a continuous background task.
        """
        logger.info("Scheduler loop starting")

        try:
            # TR-024: Set up the scheduled digest
            self.schedule_digest()

            # TR-024: Continuous loop to check for pending scheduled tasks
            while True:
                try:
                    # Check for pending scheduled tasks
                    schedule.run_pending()

                    # TR-024: Sleep for 60 seconds before next check
                    await asyncio.sleep(60)

                except Exception as e:
                    logger.error(f"Error in scheduler loop iteration: {e}")
                    # Continue running even if one iteration fails
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
            raise

        except Exception as e:
            logger.error(f"Fatal error in scheduler loop: {e}")
            raise SchedulerError(f"Scheduler loop failed: {e}")


def start_bot_with_scheduler():
    """
    Start the Discord bot with integrated scheduler

    Requirements:
    - TR-024: Scheduler integration with Discord bot
    - TR-029: Console Logging
    - TR-030: Exception Handling
    - TR-032: Credential Management
    - TR-033: Input Validation

    This is the main entry point when running with scheduled digests.
    """
    logger.info("Starting bot with scheduler")

    # TR-033: Validate configuration before starting
    try:
        config.validate_configuration()
    except config.ConfigurationError as e:
        logger.error(f"Configuration validation failed: {e}")
        return

    # Initialize scheduler
    try:
        scheduler = DigestScheduler()
    except SchedulerError as e:
        logger.error(f"Failed to create scheduler: {e}")
        return

    # TR-024: Set up bot event handler with scheduler
    @bot.event
    async def on_ready():
        """
        Event handler for when the bot is ready

        Requirements:
        - TR-029: Console Logging
        - TR-024: Start scheduler on bot ready
        """
        # TR-029: Log connection status
        logger.info(f'{bot.user} has connected to Discord!')
        logger.info(f'Bot is in {len(bot.guilds)} guild(s)')

        # Log configuration status
        config.log_configuration_status()

        # TR-024: Start the scheduler as a background task
        try:
            bot.loop.create_task(scheduler.start_scheduler())
            logger.info("Scheduler task created successfully")
        except Exception as e:
            logger.error(f"Failed to create scheduler task: {e}")

    # TR-033: Validate Discord token
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error("Please configure DISCORD_TOKEN in .env file")
        return

    try:
        # TR-004: Run bot with token
        logger.info("Starting Discord bot with scheduler...")
        bot.run(config.DISCORD_TOKEN, log_handler=None)  # Use our custom logging

    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")

    except Exception as e:
        logger.error(f"Failed to start bot with scheduler: {e}", exc_info=True)


if __name__ == '__main__':
    start_bot_with_scheduler()
