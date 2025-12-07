# Payment News Discord Bot - Requirements Document

## Document Information
- **Project Name:** Payment News Discord Bot
- **Version:** 1.0
- **Last Updated:** December 7, 2025
- **Status:** Production - Deployed on Railway

---

## 1. Business Requirements

### 1.1 Project Overview
The Payment News Discord Bot helps payment industry professionals stay informed about the latest developments in fintech and payments. The bot automatically gathers news from trusted sources, summarizes articles using AI, and delivers them directly to a Discord channel, saving users time and ensuring they never miss important industry updates.

### 1.2 Business Objectives

**BR-001: Automated News Aggregation**
The system shall automatically collect payment industry news from multiple RSS feed sources to provide comprehensive coverage of the industry without manual intervention.

**BR-002: Intelligent Content Processing**
The system shall use artificial intelligence to summarize lengthy articles into 2-3 concise sentences, allowing users to quickly understand key points without reading full articles.

**BR-003: Geographic Categorization**
The system shall categorize news articles as either "Global" or "Thailand-specific" to help users prioritize content relevant to their geographic focus.

**BR-004: Scheduled Information Delivery**
The system shall deliver a curated news digest to users at 8:00 AM Bangkok time every day, ensuring users receive timely updates at the start of their business day.

**BR-005: On-Demand Access**
The system shall allow users to request news digests at any time through manual commands, providing flexibility for users who need immediate updates.

**BR-006: Content Deduplication**
The system shall prevent duplicate articles from being shown to users, ensuring each news item is presented only once and maintaining a clean, professional user experience.

**BR-007: Historical Access**
The system shall maintain a history of previously fetched articles, allowing users to review recent news they may have missed.

### 1.3 User Stories

**US-001: Daily Digest Consumer**
As a payment industry professional, I want to receive a daily digest of payment news every morning so that I can stay informed about industry developments without spending time searching multiple websites.

**US-002: On-Demand News Requester**
As a user monitoring breaking news, I want to manually request the latest articles at any time so that I can get immediate updates when important events occur.

**US-003: Historical Reader**
As a user who missed previous updates, I want to view recently published articles so that I can catch up on news I may have overlooked.

**US-004: Geographic Filter User**
As a Thailand-based payment professional, I want articles categorized by geographic relevance so that I can prioritize Thailand-specific news that directly impacts my business.

### 1.4 Success Criteria

**SC-001:** Users receive at least one daily digest containing new articles when available.

**SC-002:** Article summaries accurately represent the original content and are comprehensible within 2-3 sentences.

**SC-003:** Manual digest requests complete within 60 seconds for up to 50 articles.

**SC-004:** No duplicate articles appear in digests or latest article listings.

**SC-005:** Geographic categorization achieves at least 90% accuracy in distinguishing Thailand-specific from global news.

---

## 2. Technical Requirements

### 2.1 System Architecture

**TR-001: Programming Language**
The system shall be implemented using Python 3.9 or higher to ensure compatibility with all required libraries and modern language features.

**TR-002: Modular Design**
The system shall be structured into separate modules with distinct responsibilities:
- `bot.py`: Discord bot initialization, command handlers, and message management
- `news_fetcher.py`: RSS feed parsing and AI processing logic
- `database.py`: Data persistence and retrieval operations
- `scheduler.py`: Automated task scheduling and execution
- `config.py`: Centralized configuration management

**TR-003: Asynchronous Processing**
The system shall use asynchronous programming patterns (asyncio) for Discord bot operations to handle concurrent connections and prevent blocking operations.

### 2.2 External Dependencies

**TR-004: Discord Integration**
The system shall use discord.py version 2.3.2 or higher with the following configuration:
- Message content intent enabled for reading user commands
- Command prefix: `!`
- Support for guild (server) and channel-specific operations
- Automatic reconnection on network failures

**TR-005: RSS Feed Parser**
The system shall use feedparser version 6.0.10 or higher to parse RSS/Atom feeds with support for:
- Standard RSS 2.0 format
- Atom feed format
- Malformed feed tolerance
- Entry deduplication by URL

**TR-006: AI Integration**
The system shall integrate with Anthropic's Claude API using the anthropic SDK version 0.18.0 or higher with the following specifications:
- Model: claude-3-5-sonnet-20240620
- Max tokens per request: 300
- Request timeout: 30 seconds
- Retry logic: 3 attempts with exponential backoff

**TR-007: Supporting Libraries**
The system shall utilize the following additional libraries:
- python-dotenv (≥1.0.0): Environment variable management
- pytz (≥2024.1): Timezone handling for Bangkok time (Asia/Bangkok)
- aiohttp (≥3.9.1): Asynchronous HTTP client
- beautifulsoup4 (≥4.12.0): HTML parsing for future web scraping features
- schedule (≥1.2.0): Task scheduling

### 2.3 Data Management

**TR-008: Database System**
The system shall use SQLite 3 for data persistence with the following specifications:
- Database file: `payment_news.db`
- Single-file database located in project root directory
- No external database server required
- ACID compliance for data integrity

**TR-009: Database Schema**
The system shall implement an `articles` table with the following structure:

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,              -- Article URL (unique constraint)
    title TEXT NOT NULL,                    -- Article headline
    source TEXT NOT NULL,                   -- RSS feed source name
    published_date TEXT,                    -- Original publication date (ISO 8601)
    summary TEXT,                           -- AI-generated summary
    category TEXT,                          -- "Global" or "Thailand-specific"
    fetched_date TEXT NOT NULL,            -- Timestamp when article was fetched
    sent_in_digest INTEGER DEFAULT 0       -- Flag: 0=unsent, 1=sent
)
```

**TR-010: Data Constraints**
- URL field must be unique to prevent duplicate articles
- Articles with identical URLs shall be rejected during insertion
- Fetched_date shall be stored in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- sent_in_digest flag shall be updated atomically after successful digest delivery

**TR-011: Data Retention**
The system shall retain all articles indefinitely in the database with no automatic purging mechanism. Manual database cleanup is the responsibility of the system administrator.

### 2.4 Configuration Management

**TR-012: Environment Variables**
The system shall load sensitive configuration from a `.env` file with the following required variables:
- `DISCORD_TOKEN`: Discord bot authentication token (string)
- `DISCORD_CHANNEL_ID`: Target channel ID for posting digests (integer)
- `ANTHROPIC_API_KEY`: Anthropic API authentication key (string, format: sk-ant-*)

**TR-013: Application Configuration**
The system shall define the following configurable parameters in `config.py`:
- RSS_FEEDS: List of dictionaries containing feed name and URL
- DIGEST_TIME: Daily digest schedule time (format: "HH:MM")
- TIMEZONE: Target timezone (default: "Asia/Bangkok")
- DATABASE_PATH: SQLite database file path
- COMMAND_PREFIX: Discord command prefix (default: "!")
- MAX_ARTICLES_LATEST: Number of articles returned by `!latest` command (default: 5)

### 2.5 RSS Feed Processing

**TR-014: Feed Sources**
The system shall fetch articles from the following RSS feeds:
- Finextra Payments: `https://www.finextra.com/rss/channel.aspx?channel=payments`
- Payments Dive: `https://www.paymentsdive.com/feeds/news/`

**TR-015: Feed Parsing Logic**
For each RSS feed entry, the system shall extract:
- `entry.title`: Article headline (fallback: "No Title")
- `entry.link`: Article URL
- `entry.published`: Publication date (fallback: empty string)
- `entry.description` or `entry.summary`: Article description

**TR-016: Feed Processing Workflow**
1. Parse RSS feed using feedparser
2. Iterate through all entries in the feed
3. Check if article URL exists in database
4. If URL is new, extract article data and add to processing queue
5. Handle parsing errors gracefully without crashing the application
6. Log errors to console for debugging

### 2.6 AI Processing

**TR-017: Summarization Prompt**
The system shall use the following prompt structure for Claude API:

```
Analyze this payment industry news article:

Title: {article_title}
Description: {article_description}

Please provide:
1. A concise 2-3 sentence summary
2. Categorize as either "Global" or "Thailand-specific"

Format your response as:
SUMMARY: [your summary here]
CATEGORY: [Global or Thailand-specific]
```

**TR-018: Response Parsing**
The system shall parse Claude API responses by:
- Splitting response text by newline characters
- Extracting text after "SUMMARY:" prefix
- Extracting text after "CATEGORY:" prefix
- Trimming whitespace from extracted values

**TR-019: Error Handling for AI Processing**
If Claude API request fails or times out, the system shall:
- Use the first 200 characters of article description as fallback summary
- Default category to "Global"
- Log the error with article URL for manual review
- Continue processing remaining articles

**TR-020: Rate Limiting**
The system shall implement the following rate limiting measures:
- Process articles sequentially (not in parallel) to respect API rate limits
- Wait for each API response before processing next article
- Implement exponential backoff on 429 (Too Many Requests) errors

### 2.7 Discord Bot Commands

**TR-021: Command - !digest**
The system shall implement a `!digest` command with the following behavior:

**Trigger:** User types `!digest` in any channel where bot has read permissions

**Process:**
1. Send acknowledgment message: "Fetching and processing latest news... This may take a moment."
2. Fetch new articles from all configured RSS feeds
3. Process each new article through Claude API for summary and categorization
4. Store processed articles in database
5. Retrieve all unsent articles from database
6. Generate formatted digest using `create_digest()` method
7. Send digest to channel (split into multiple messages if > 2000 characters)
8. Mark all sent articles with `sent_in_digest = 1`
9. Send completion message: "✅ Digest complete! Processed X new articles."

**Error Handling:**
- If no new articles found: Send "No new articles to report."
- If exception occurs: Send "❌ Error generating digest: {error_message}"
- Log all errors to console with full stack trace

**TR-022: Command - !latest**
The system shall implement a `!latest` command with the following behavior:

**Trigger:** User types `!latest` in any channel where bot has read permissions

**Process:**
1. Query database for last 5 articles ordered by fetched_date DESC
2. Format each article using `format_article_for_discord()` method
3. Send articles in a single message (or multiple if > 2000 characters)
4. Include header: "📰 Latest {count} Articles"

**Error Handling:**
- If database is empty: Send "No articles found in the database."
- If exception occurs: Send "❌ Error fetching latest articles: {error_message}"

**TR-023: Message Length Handling**
The system shall split messages exceeding Discord's 2000 character limit using the following algorithm:
1. Split digest text by newline characters
2. Accumulate lines into current chunk
3. If adding next line exceeds 2000 characters, send current chunk and start new chunk
4. Send remaining content as final chunk

### 2.8 Scheduled Digest

**TR-024: Scheduling Mechanism**
The system shall use the `schedule` library to execute daily digest at configured time:
- Schedule task to run every day at DIGEST_TIME (default: "08:00")
- Check for pending scheduled tasks every 60 seconds
- Execute tasks asynchronously in Discord bot event loop

**TR-025: Scheduled Digest Process**
The automated digest shall execute the following workflow:
1. Fetch and process new articles from all RSS feeds
2. Retrieve unsent articles from database
3. If no articles found, log "No new articles for scheduled digest" and exit
4. Retrieve Discord channel object using DISCORD_CHANNEL_ID
5. If channel not found, log error and exit
6. Generate formatted digest
7. Send digest to channel (split if necessary)
8. Mark articles as sent in database
9. Log "Scheduled digest sent! Processed X new articles."

**TR-026: Timezone Handling**
The system shall use pytz to ensure digest timing aligns with Asia/Bangkok timezone regardless of server's local timezone.

### 2.9 Message Formatting

**TR-027: Article Format**
Each article in a digest shall be formatted as follows:

```
{category_emoji} **{article_title}**
*Source: {source_name}*
{ai_summary}
[Read more]({article_url})

```

Where:
- category_emoji = "🌏" if category is "Global"
- category_emoji = "🇹🇭" if category is "Thailand-specific"
- article_title is in bold using Discord markdown
- source_name is in italics
- article_url is a clickable hyperlink

**TR-028: Digest Format**
A complete digest shall be formatted as follows:

```
**📰 Payment Industry News Digest - {Month Day, Year}**

**🇹🇭 THAILAND-SPECIFIC NEWS**
{thailand_articles}

**🌏 GLOBAL NEWS**
{global_articles}
```

Where:
- Date is formatted as "December 06, 2025"
- Thailand-specific articles appear before global articles
- Section headers omitted if no articles in that category

### 2.10 Error Handling and Logging

**TR-029: Console Logging**
The system shall log the following events to console:
- Bot connection status: "{bot_user} has connected to Discord!"
- Guild count: "Bot is in {count} guild(s)"
- Schedule confirmation: "Scheduled daily digest at {time} {timezone}"
- Digest completion: "Scheduled digest sent! Processed {count} new articles."
- Feed fetch errors: "Error fetching from {feed_name}: {error}"
- AI processing errors: "Error processing article with AI: {error}"
- Channel errors: "Channel {channel_id} not found"

**TR-030: Exception Handling**
The system shall catch and handle exceptions at the following levels:
- Command level: Catch all exceptions in command handlers, send error message to user
- Feed level: Catch feed parsing errors, log and continue with next feed
- Article level: Catch AI processing errors, use fallback values and continue
- Database level: Catch integrity errors on duplicate URLs, silently skip

**TR-031: Discord API Error Handling**
The system shall gracefully handle Discord API errors:
- Insufficient permissions: Log error with channel/guild info
- Rate limiting (429): Implement exponential backoff
- Gateway disconnection: Automatic reconnection via discord.py

### 2.11 Security Requirements

**TR-032: Credential Management**
- All API keys and tokens shall be stored in `.env` file
- `.env` file shall be excluded from version control via `.gitignore`
- No credentials shall be hardcoded in source code
- `.env.example` template shall contain placeholder values only

**TR-033: Input Validation**
- DISCORD_CHANNEL_ID shall be validated as integer
- Configuration values shall have sensible defaults if environment variables are missing
- Article URLs shall be used as-is without modification

**TR-034: Dependency Security**
- All dependencies shall be pinned to specific minimum versions
- Dependencies shall be reviewed for known vulnerabilities before deployment
- Regular updates to dependencies as security patches are released

### 2.12 Performance Requirements

**TR-035: Response Time**
- `!latest` command shall respond within 2 seconds
- `!digest` command shall complete within 60 seconds for up to 50 articles
- Scheduled digest shall complete within 120 seconds

**TR-036: Concurrent Operations**
- Bot shall handle multiple simultaneous command requests from different users
- Discord connection shall remain stable during article processing
- Database operations shall use connection pooling for efficiency

**TR-037: Resource Usage**
- Memory usage shall remain below 500MB during normal operation
- Database file size shall grow approximately 1MB per 1000 articles
- CPU usage shall remain below 50% during article processing

### 2.13 Deployment Requirements

**TR-038: Environment Setup**
The system shall run on any platform supporting:
- Python 3.9 or higher
- Write access to local filesystem for SQLite database
- Network access to Discord API, Anthropic API, and RSS feed URLs

**TR-039: Installation Process**
1. Clone repository to target directory
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Configure environment variables in `.env`
5. Run bot: `python scheduler.py` (with scheduling) or `python bot.py` (commands only)

**TR-040: Discord Bot Permissions**
The bot shall be invited to Discord servers with the following permissions:
- Send Messages: Required for posting digests and command responses
- Read Message History: Required for reading user commands
- Message Content Intent: Required privileged intent for reading message content

### 2.14 Testing Requirements

**TR-041: Unit Testing**
Each module shall have unit tests covering:
- Database CRUD operations
- Article formatting functions
- Message splitting logic
- Configuration loading

**TR-042: Integration Testing**
The system shall be tested for:
- RSS feed fetching from live sources
- Claude API integration with real requests
- Discord bot command execution in test server
- Scheduled digest execution

**TR-043: Error Scenario Testing**
The system shall be tested against:
- Malformed RSS feeds
- Claude API timeout/errors
- Discord API rate limiting
- Database connection failures
- Invalid configuration values

### 2.15 Maintenance Requirements

**TR-044: RSS Feed Updates**
When RSS feed URLs change:
1. Update URL in `config.py` RSS_FEEDS list
2. Test new feed URL with feedparser
3. Restart bot to load new configuration
4. Verify articles are fetched correctly

**TR-045: Database Maintenance**
Database maintenance procedures:
- Backup: `cp payment_news.db payment_news.db.backup`
- Reset sent flags: `UPDATE articles SET sent_in_digest = 0`
- Clear database: Delete `payment_news.db` file (will auto-recreate)

**TR-046: Monitoring**
System administrators shall monitor:
- Bot uptime and connection status
- Daily digest delivery confirmation in logs
- Database file size growth
- Error messages in console output

---

## 3. Non-Functional Requirements

### 3.1 Reliability
**NFR-001:** The system shall maintain 99% uptime during business hours (8 AM - 6 PM Bangkok time).

**NFR-002:** The system shall automatically reconnect to Discord on network interruptions.

**NFR-003:** Failed API requests shall not crash the application.

### 3.2 Maintainability
**NFR-004:** Code shall follow PEP 8 style guidelines for Python.

**NFR-005:** Each function shall have a docstring describing its purpose.

**NFR-006:** Configuration changes shall not require code modifications.

### 3.3 Usability
**NFR-007:** Command syntax shall be simple and memorable (single word after prefix).

**NFR-008:** Error messages shall be user-friendly and actionable.

**NFR-009:** Digest formatting shall be readable on mobile and desktop Discord clients.

### 3.4 Scalability
**NFR-010:** The system shall support addition of new RSS feeds without code refactoring.

**NFR-011:** Database shall efficiently handle up to 100,000 articles without performance degradation.

**NFR-012:** The system shall process up to 100 articles in a single digest run.

---

## 4. Constraints and Assumptions

### 4.1 Constraints
**C-001:** Discord message length limited to 2000 characters per message.

**C-002:** Anthropic API usage subject to account rate limits and billing.

**C-003:** RSS feeds must be publicly accessible without authentication.

**C-004:** Bot requires continuous internet connectivity to function.

### 4.2 Assumptions
**A-001:** RSS feed sources will maintain consistent XML/Atom format.

**A-002:** Discord bot token and Anthropic API key remain valid.

**A-003:** Target Discord channel allows bot to send messages.

**A-004:** Server running the bot maintains accurate system time.

**A-005:** Claude API will categorize Thailand-specific news with reasonable accuracy.

---

## 5. Future Enhancements

### 5.1 Planned Features (Not in Current Scope)
**FE-001:** Reaction-based article saving to user-specific collections

**FE-002:** Search functionality for historical articles by keyword

**FE-003:** Category filter commands (`!thailand`, `!global`)

**FE-004:** Weekly digest summarizing top articles

**FE-005:** Custom notification alerts for specific keywords or topics

**FE-006:** User preference management for personalized content

**FE-007:** Web scraping for non-RSS news sources

**FE-008:** Sentiment analysis and trend detection

**FE-009:** Multi-language support for non-English articles

**FE-010:** Integration with additional messaging platforms (Slack, Telegram)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | System | Initial requirements document created |

---

## Approval

**Business Owner:** ___________________________ Date: ___________

**Technical Lead:** ___________________________ Date: ___________

**Project Manager:** ___________________________ Date: ___________
