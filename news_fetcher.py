"""
News Fetcher Module

This module handles RSS feed fetching, AI processing, and article formatting.
Implements rate limiting and retry logic for external API calls.

Requirements:
- TR-005: RSS Feed Parser
- TR-006: AI Integration
- TR-014: Feed Sources
- TR-015: Feed Parsing Logic
- TR-016: Feed Processing Workflow
- TR-017: Summarization Prompt
- TR-018: Response Parsing
- TR-019: Error Handling for AI Processing
- TR-020: Rate Limiting
- TR-027: Article Format
- TR-028: Digest Format
"""

import feedparser
import anthropic
import logging
import time
import re
import discord
from typing import List, Dict, Union
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import config
from database import NewsDatabase

# Configure logging - TR-029: Console Logging
logger = logging.getLogger(__name__)


class NewsFetcherError(Exception):
    """Raised when news fetching operations fail"""
    pass


class NewsFetcher:
    """
    Handles RSS feed fetching and AI processing of news articles

    Requirements:
    - TR-005: RSS Feed Parser (feedparser)
    - TR-006: AI Integration (Anthropic)
    """

    def __init__(self):
        """
        Initialize news fetcher with Anthropic client and database

        Requirements:
        - TR-006: AI Integration with Anthropic SDK
        - TR-008: Database connection
        """
        # TR-006: Validate API key before creating client
        if not config.ANTHROPIC_API_KEY:
            logger.error("Anthropic API key not configured")
            raise NewsFetcherError("ANTHROPIC_API_KEY is required")

        try:
            self.client = anthropic.Anthropic(
                api_key=config.ANTHROPIC_API_KEY,
                timeout=config.API_REQUEST_TIMEOUT  # TR-006: Request timeout
            )
            self.db = NewsDatabase()
            logger.info("News fetcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize news fetcher: {e}")
            raise NewsFetcherError(f"Initialization failed: {e}")

    def sanitize_text(self, text: str, max_length: int = 10000) -> str:
        """
        Sanitize and truncate text input

        Requirements: TR-033: Input Validation

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            str: Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove null bytes and other problematic characters
        text = text.replace('\x00', '').strip()

        # Truncate if too long
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]

        return text

    def strip_html(self, text: str) -> str:
        """
        Strip HTML tags from text

        Requirements: TR-033: Input Validation

        Args:
            text: Text potentially containing HTML

        Returns:
            str: Plain text with HTML removed
        """
        if not text:
            return ""

        try:
            # Parse HTML and extract text
            soup = BeautifulSoup(text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text and clean up whitespace
            text = soup.get_text()

            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())

            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

            # Drop blank lines
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.warning(f"Error stripping HTML: {e}")
            # Fallback: simple regex to remove tags
            return re.sub(r'<[^>]+>', '', text)

    def clean_url(self, url: str) -> str:
        """
        Remove tracking parameters from URLs

        Requirements: TR-033: Input Validation

        Args:
            url: URL potentially containing tracking parameters

        Returns:
            str: Cleaned URL without tracking parameters
        """
        if not url:
            return url

        try:
            # Common tracking parameters to remove
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'msclkid', 'mc_cid', 'mc_eid',
                '_ga', '_gac', '_gl', 'ref', 'referrer', 'source'
            }

            # Parse URL
            parsed = urlparse(url)

            # Parse query parameters
            params = parse_qs(parsed.query, keep_blank_values=True)

            # Remove tracking parameters
            cleaned_params = {
                key: value for key, value in params.items()
                if key.lower() not in tracking_params
            }

            # Rebuild query string
            cleaned_query = urlencode(cleaned_params, doseq=True)

            # Rebuild URL
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                cleaned_query,
                parsed.fragment
            ))

            return cleaned_url

        except Exception as e:
            logger.warning(f"Error cleaning URL: {e}")
            return url

    def fetch_rss_feeds(self) -> List[Dict]:
        """
        Fetch articles from all configured RSS feeds

        Requirements:
        - TR-014: Feed Sources
        - TR-015: Feed Parsing Logic
        - TR-016: Feed Processing Workflow
        - TR-030: Exception Handling

        Returns:
            List of article dictionaries
        """
        all_articles = []

        # TR-014: Iterate through configured RSS feeds
        for feed_config in config.RSS_FEEDS:
            feed_name = feed_config.get('name', 'Unknown')
            feed_url = feed_config.get('url', '')

            if not feed_url:
                logger.warning(f"Skipping feed '{feed_name}': No URL configured")
                continue

            try:
                # TR-005, TR-015: Parse RSS feed
                logger.info(f"Fetching RSS feed: {feed_name}")
                feed = feedparser.parse(feed_url)

                # Check for feed errors
                if hasattr(feed, 'bozo') and feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_name}: {feed.get('bozo_exception', 'Unknown error')}")

                # TR-015: Extract article data from each entry
                for entry in feed.entries:
                    try:
                        # TR-015: Extract required fields with fallbacks
                        title = entry.get('title', 'No Title')
                        url = entry.get('link', '')
                        published = entry.get('published', '')
                        description = entry.get('description', entry.get('summary', ''))

                        # TR-033: Validate article URL
                        if not url or not url.startswith(('http://', 'https://')):
                            logger.debug(f"Skipping article with invalid URL: {url}")
                            continue

                        # Strip HTML from description and clean URL
                        clean_description = self.strip_html(description)
                        clean_url = self.clean_url(url.strip())

                        # TR-033: Sanitize text fields
                        article = {
                            'title': self.sanitize_text(title, 500),
                            'url': clean_url,
                            'source': feed_name,
                            'published': published,
                            'description': self.sanitize_text(clean_description, 5000)
                        }

                        # TR-016: Check for duplicates before adding
                        if article['url'] and not self.db.article_exists(article['url']):
                            all_articles.append(article)
                            logger.debug(f"New article found: {article['title'][:50]}...")
                        else:
                            logger.debug(f"Duplicate article skipped: {article['url']}")

                    except Exception as e:
                        logger.warning(f"Error parsing entry from {feed_name}: {e}")
                        continue

                logger.info(f"Fetched {len([a for a in all_articles if a['source'] == feed_name])} new articles from {feed_name}")

            except Exception as e:
                # TR-030: Handle feed fetch errors gracefully
                logger.error(f"Error fetching from {feed_name}: {e}")
                continue

        logger.info(f"Total new articles fetched: {len(all_articles)}")
        return all_articles

    def process_article_with_ai(self, article: Dict) -> Dict:
        """
        Use Anthropic API to summarize and categorize the article

        Requirements:
        - TR-006: AI Integration
        - TR-017: Summarization Prompt
        - TR-018: Response Parsing
        - TR-019: Error Handling for AI Processing
        - TR-020: Rate Limiting

        Args:
            article: Article dictionary with title and description

        Returns:
            Article dictionary with added summary and category
        """
        # TR-017: Construct prompt for AI processing
        prompt = f"""Analyze this payment industry news article:

Title: {article['title']}
Description: {article['description']}

Please provide:
1. A concise 2-3 sentence summary
2. Categorize as either "Global" or "Thailand-specific"

Format your response as:
SUMMARY: [your summary here]
CATEGORY: [Global or Thailand-specific]"""

        # TR-020: Implement retry logic with exponential backoff
        max_retries = config.API_MAX_RETRIES
        retry_delay = config.API_RETRY_DELAY

        for attempt in range(max_retries):
            try:
                # TR-006: Call Anthropic API
                logger.debug(f"Processing article with AI (attempt {attempt + 1}/{max_retries}): {article['title'][:50]}...")

                message = self.client.messages.create(
                    model=config.ANTHROPIC_MODEL,  # TR-006: Use configured model
                    max_tokens=config.ANTHROPIC_MAX_TOKENS,  # TR-006: Token limit
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                response_text = message.content[0].text

                # TR-018: Parse the AI response
                summary = ""
                category = "Global"  # Default category

                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('SUMMARY:'):
                        summary = line.replace('SUMMARY:', '').strip()
                    elif line.startswith('CATEGORY:'):
                        category_raw = line.replace('CATEGORY:', '').strip()
                        # Validate category
                        if category_raw in ['Global', 'Thailand-specific']:
                            category = category_raw
                        else:
                            logger.warning(f"Invalid category '{category_raw}', defaulting to 'Global'")

                # TR-018: Use fallback if summary not found
                if not summary:
                    logger.warning("AI did not provide summary, using description fallback")
                    summary = article['description'][:200] if article['description'] else "No summary available"

                article['summary'] = summary
                article['category'] = category

                logger.debug(f"Article processed successfully: Category={category}")
                return article

            except anthropic.APIError as e:
                # TR-019: Handle API errors with retry logic
                logger.warning(f"Anthropic API error (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    # TR-020: Exponential backoff
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    # Final attempt failed, use fallback
                    logger.error(f"Failed to process article after {max_retries} attempts")
                    article['summary'] = article['description'][:200] if article['description'] else "No summary available"
                    article['category'] = "Global"
                    return article

            except Exception as e:
                # TR-030: Handle unexpected errors
                logger.error(f"Unexpected error processing article with AI: {e}")
                article['summary'] = article['description'][:200] if article['description'] else "No summary available"
                article['category'] = "Global"
                return article

        return article

    def fetch_and_process_news(self) -> int:
        """
        Fetch new articles, process them with AI, and store in database

        Requirements:
        - TR-016: Feed Processing Workflow
        - TR-020: Rate Limiting (sequential processing)
        - TR-030: Exception Handling

        Returns:
            int: Number of articles successfully processed
        """
        logger.info("Starting news fetch and process operation")

        try:
            # TR-016: Fetch articles from RSS feeds
            articles = self.fetch_rss_feeds()
            processed_count = 0

            if not articles:
                logger.info("No new articles to process")
                return 0

            # TR-020: Process articles sequentially to respect rate limits
            for idx, article in enumerate(articles, 1):
                logger.info(f"Processing article {idx}/{len(articles)}: {article['title'][:50]}...")

                try:
                    # Process with AI
                    processed_article = self.process_article_with_ai(article)

                    # Store in database
                    success = self.db.add_article(
                        url=processed_article['url'],
                        title=processed_article['title'],
                        source=processed_article['source'],
                        published_date=processed_article.get('published'),
                        summary=processed_article['summary'],
                        category=processed_article['category']
                    )

                    if success:
                        processed_count += 1
                        logger.debug(f"Article stored successfully: {processed_article['title'][:50]}...")
                    else:
                        logger.debug(f"Article not stored (likely duplicate): {processed_article['title'][:50]}...")

                except Exception as e:
                    logger.error(f"Error processing article: {e}")
                    continue

            logger.info(f"News fetch and process complete: {processed_count} articles added")
            return processed_count

        except Exception as e:
            logger.error(f"Error in fetch_and_process_news: {e}")
            raise NewsFetcherError(f"Failed to fetch and process news: {e}")

    def format_article_for_discord(self, article: Dict) -> discord.Embed:
        """
        Format a single article as Discord embed

        Requirements:
        - TR-027: Article Format
        - TR-033: Input Validation

        Args:
            article: Article dictionary

        Returns:
            discord.Embed: Formatted article embed
        """
        try:
            # TR-027: Determine category emoji and color
            category = article.get('category', 'Global')
            category_emoji = "🌏" if category == "Global" else "🇹🇭"

            # Color coding: Blue for Global, Orange for Thailand
            embed_color = 0x3498db if category == "Global" else 0xe67e22

            # TR-033: Sanitize and validate fields
            title = self.sanitize_text(article.get('title', 'No Title'), 256)  # Discord limit
            source = self.sanitize_text(article.get('source', 'Unknown'), 100)
            summary = self.sanitize_text(article.get('summary', 'No summary available'), 2048)  # Discord limit
            url = article.get('url', '').strip()

            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://example.com'  # Fallback URL

            # Create embed
            embed = discord.Embed(
                title=f"{category_emoji} {title}",
                description=summary,
                url=url,
                color=embed_color
            )

            # Add source as footer
            embed.set_footer(text=f"Source: {source}")

            # Add timestamp if available
            if article.get('published_date'):
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(article['published_date'])
                    embed.timestamp = pub_date
                except:
                    pass

            return embed

        except Exception as e:
            logger.error(f"Error formatting article embed: {e}")
            # Return error embed
            error_embed = discord.Embed(
                title="Error",
                description="Error formatting article",
                color=0xe74c3c
            )
            return error_embed

    def create_digest(self, articles: List[Dict]) -> Dict[str, Union[str, List[discord.Embed]]]:
        """
        Create a formatted digest from multiple articles

        Requirements:
        - TR-028: Digest Format
        - TR-030: Exception Handling

        Args:
            articles: List of article dictionaries

        Returns:
            dict: Dictionary containing header text and lists of embeds by category
        """
        if not articles:
            return {
                'header': "No new articles to report.",
                'thailand_embeds': [],
                'global_embeds': []
            }

        try:
            # TR-028: Separate articles by category
            global_articles = [a for a in articles if a.get('category') == "Global"]
            thailand_articles = [a for a in articles if a.get('category') == "Thailand-specific"]

            # TR-028: Create digest header with date
            header = f"📰 **Payment Industry News Digest - {datetime.now().strftime('%B %d, %Y')}**"

            # Create embeds for Thailand-specific articles
            thailand_embeds = []
            if thailand_articles:
                for article in thailand_articles:
                    embed = self.format_article_for_discord(article)
                    thailand_embeds.append(embed)

            # Create embeds for global articles
            global_embeds = []
            if global_articles:
                for article in global_articles:
                    embed = self.format_article_for_discord(article)
                    global_embeds.append(embed)

            logger.info(f"Digest created: {len(thailand_articles)} Thailand-specific, {len(global_articles)} Global articles")

            return {
                'header': header,
                'thailand_embeds': thailand_embeds,
                'global_embeds': global_embeds
            }

        except Exception as e:
            logger.error(f"Error creating digest: {e}")
            return {
                'header': f"Error creating digest: {str(e)}",
                'thailand_embeds': [],
                'global_embeds': []
            }
