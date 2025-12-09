"""
Configuration Management Module

This module handles all configuration loading and validation for the Payment News Bot.
All sensitive credentials are loaded from environment variables.

Requirements:
- TR-012: Environment Variables
- TR-013: Application Configuration
- TR-032: Credential Management
- TR-033: Input Validation
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging - TR-029: Console Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)-8s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# TR-032: Load environment variables from .env file (if it exists)
# In production (Railway), environment variables are set directly by the platform
load_dotenv(override=False)  # Don't override existing env vars


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


def validate_discord_token(token):
    """
    Validate Discord bot token format

    Requirements: TR-033: Input Validation

    Args:
        token: Discord bot token string

    Returns:
        bool: True if valid, False otherwise
    """
    if not token:
        return False

    # Discord tokens are typically base64 encoded and contain periods
    if len(token) < 50:  # Minimum reasonable token length
        return False

    return True


def validate_anthropic_api_key(api_key):
    """
    Validate Anthropic API key format

    Requirements: TR-033: Input Validation

    Args:
        api_key: Anthropic API key string

    Returns:
        bool: True if valid, False otherwise
    """
    if not api_key:
        return False

    # Anthropic keys start with 'sk-ant-'
    if not api_key.startswith('sk-ant-'):
        logger.warning("Anthropic API key does not start with expected prefix 'sk-ant-'")
        return False

    if len(api_key) < 20:  # Minimum reasonable key length
        return False

    return True


def validate_channel_id(channel_id):
    """
    Validate Discord channel ID

    Requirements: TR-033: Input Validation

    Args:
        channel_id: Discord channel ID (integer or string)

    Returns:
        int: Validated channel ID

    Raises:
        ConfigurationError: If channel ID is invalid
    """
    try:
        channel_id_int = int(channel_id) if channel_id else 0

        if channel_id_int <= 0:
            raise ConfigurationError("DISCORD_CHANNEL_ID must be a positive integer")

        # Discord snowflake IDs are 64-bit integers
        if channel_id_int > 2**63 - 1:
            raise ConfigurationError("DISCORD_CHANNEL_ID exceeds maximum value")

        return channel_id_int

    except (ValueError, TypeError):
        raise ConfigurationError(f"DISCORD_CHANNEL_ID must be a valid integer, got: {channel_id}")


# TR-012: Load and validate Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID_RAW = os.getenv('DISCORD_CHANNEL_ID', '0')

# TR-033: Validate Discord credentials
if not validate_discord_token(DISCORD_TOKEN):
    logger.error("Invalid or missing DISCORD_TOKEN in environment variables")
    logger.error("Please ensure DISCORD_TOKEN is set in .env file")
    # Don't exit here, let the bot.py handle it for better error messages

try:
    DISCORD_CHANNEL_ID = validate_channel_id(DISCORD_CHANNEL_ID_RAW)
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    DISCORD_CHANNEL_ID = 0


# TR-012: Load and validate Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# TR-033: Validate Anthropic API key
if not validate_anthropic_api_key(ANTHROPIC_API_KEY):
    logger.error("Invalid or missing ANTHROPIC_API_KEY in environment variables")
    logger.error("Please ensure ANTHROPIC_API_KEY is set in .env file")
    # Don't exit here, let the modules that use it handle the error


# TR-014: RSS Feed Sources
# TR-013: Application Configuration - RSS Feed URLs
RSS_FEEDS = [
    {
        'name': 'Finextra Payments',
        'url': 'https://www.finextra.com/rss/channel.aspx?channel=payments'
    },
    {
        'name': 'Payments Dive',
        'url': 'https://www.paymentsdive.com/feeds/news/'
    }
]

# TR-024: Schedule Configuration
# TR-026: Timezone Handling
DIGEST_TIME = '08:00'  # 8 AM Bangkok time
TIMEZONE = 'Asia/Bangkok'

# TR-008: Database Configuration
DATABASE_PATH = 'payment_news.db'

# TR-021, TR-022: Bot Command Configuration
COMMAND_PREFIX = '!'
MAX_ARTICLES_LATEST = 5  # TR-022: Maximum articles for !latest command

# TR-020: Rate Limiting Configuration
API_REQUEST_TIMEOUT = 30  # seconds - TR-006: Request timeout
API_MAX_RETRIES = 3  # TR-006: Retry logic
API_RETRY_DELAY = 1  # seconds, will use exponential backoff

# TR-006: AI Integration Configuration
ANTHROPIC_MODEL = 'claude-3-5-sonnet-20241022'  # Latest stable version
ANTHROPIC_MAX_TOKENS = 300

# TR-023: Discord Message Length Limit
DISCORD_MAX_MESSAGE_LENGTH = 2000

# TR-035: Performance Requirements - Timeout values
DIGEST_TIMEOUT = 120  # seconds
LATEST_TIMEOUT = 2  # seconds

# Validate critical configuration at import time
def validate_configuration():
    """
    Validate all critical configuration settings

    Requirements: TR-033: Input Validation

    Raises:
        ConfigurationError: If any critical configuration is invalid
    """
    errors = []

    if not DISCORD_TOKEN:
        errors.append("DISCORD_TOKEN is required")

    if DISCORD_CHANNEL_ID <= 0:
        errors.append("DISCORD_CHANNEL_ID must be a positive integer")

    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is required")

    if not RSS_FEEDS or len(RSS_FEEDS) == 0:
        errors.append("At least one RSS feed must be configured")

    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigurationError(error_msg)

    logger.info("Configuration validation successful")


# Log configuration status (without exposing secrets)
def log_configuration_status():
    """
    Log configuration status without exposing sensitive information

    Requirements: TR-029: Console Logging, TR-032: Credential Management
    """
    logger.info("Configuration loaded:")
    logger.info(f"  Discord Token: {'✓ Set' if DISCORD_TOKEN else '✗ Missing'}")
    logger.info(f"  Discord Channel ID: {DISCORD_CHANNEL_ID if DISCORD_CHANNEL_ID > 0 else '✗ Invalid'}")
    logger.info(f"  Anthropic API Key: {'✓ Set' if ANTHROPIC_API_KEY else '✗ Missing'}")
    logger.info(f"  RSS Feeds: {len(RSS_FEEDS)} configured")
    logger.info(f"  Digest Time: {DIGEST_TIME} {TIMEZONE}")
    logger.info(f"  Database Path: {DATABASE_PATH}")
