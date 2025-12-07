"""
Database Management Module

This module handles all SQLite database operations for storing and retrieving news articles.
All queries use parameterized statements to prevent SQL injection.

Requirements:
- TR-008: Database System
- TR-009: Database Schema
- TR-010: Data Constraints
- TR-011: Data Retention
- TR-030: Exception Handling
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import config

# Configure logging - TR-029: Console Logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass


class NewsDatabase:
    """
    Manages SQLite database operations for news articles

    Requirements:
    - TR-008: SQLite 3 database system
    - TR-009: Database schema implementation
    """

    def __init__(self, db_path: str = config.DATABASE_PATH):
        """
        Initialize database connection and create tables if needed

        Args:
            db_path: Path to SQLite database file

        Requirements: TR-008: Database System
        """
        self.db_path = db_path
        self.init_database()
        logger.info(f"Database initialized at: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with automatic cleanup

        Requirements: TR-030: Exception Handling

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            # Enable foreign keys and other security features
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """
        Initialize the database with required tables

        Requirements:
        - TR-009: Database Schema
        - TR-010: Data Constraints (URL uniqueness)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-009: Create articles table with specified schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        source TEXT NOT NULL,
                        published_date TEXT,
                        summary TEXT,
                        category TEXT,
                        fetched_date TEXT NOT NULL,
                        sent_in_digest INTEGER DEFAULT 0,
                        CHECK (sent_in_digest IN (0, 1)),
                        CHECK (length(url) > 0),
                        CHECK (length(title) > 0),
                        CHECK (length(source) > 0)
                    )
                ''')

                # Create index for performance - TR-036: Concurrent Operations
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_sent_in_digest
                    ON articles(sent_in_digest)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_fetched_date
                    ON articles(fetched_date DESC)
                ''')

                logger.info("Database schema initialized successfully")

        except DatabaseError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def validate_article_data(self, url: str, title: str, source: str,
                             summary: str, category: str) -> bool:
        """
        Validate article data before database insertion

        Requirements: TR-033: Input Validation

        Args:
            url: Article URL
            title: Article title
            source: Feed source name
            summary: Article summary
            category: Article category

        Returns:
            bool: True if valid, False otherwise
        """
        # TR-033: Validate required fields
        if not url or not isinstance(url, str) or len(url.strip()) == 0:
            logger.warning(f"Invalid URL: {url}")
            return False

        if not title or not isinstance(title, str) or len(title.strip()) == 0:
            logger.warning(f"Invalid title for URL: {url}")
            return False

        if not source or not isinstance(source, str) or len(source.strip()) == 0:
            logger.warning(f"Invalid source for URL: {url}")
            return False

        # Validate URL format (basic check)
        if not url.startswith(('http://', 'https://')):
            logger.warning(f"URL must start with http:// or https://: {url}")
            return False

        # Validate summary
        if not summary or not isinstance(summary, str):
            logger.warning(f"Invalid summary for URL: {url}")
            return False

        # Validate category
        valid_categories = ['Global', 'Thailand-specific']
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}' for URL: {url}. Must be one of {valid_categories}")
            return False

        return True

    def article_exists(self, url: str) -> bool:
        """
        Check if an article URL already exists in the database

        Requirements:
        - TR-010: Data Constraints (deduplication)
        - TR-030: Exception Handling

        Args:
            url: Article URL to check

        Returns:
            bool: True if article exists, False otherwise
        """
        if not url:
            return False

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-010: Use parameterized query to prevent SQL injection
                cursor.execute('SELECT COUNT(*) FROM articles WHERE url = ?', (url,))
                count = cursor.fetchone()[0]

                return count > 0

        except DatabaseError as e:
            logger.error(f"Error checking if article exists: {e}")
            return False

    def add_article(self, url: str, title: str, source: str,
                   published_date: Optional[str], summary: str,
                   category: str) -> bool:
        """
        Add a new article to the database

        Requirements:
        - TR-010: Data Constraints (URL uniqueness, validation)
        - TR-030: Exception Handling (IntegrityError)
        - TR-033: Input Validation

        Args:
            url: Article URL (must be unique)
            title: Article title
            source: Feed source name
            published_date: Original publication date
            summary: AI-generated summary
            category: "Global" or "Thailand-specific"

        Returns:
            bool: True if article added successfully, False otherwise
        """
        # TR-033: Validate input data
        if not self.validate_article_data(url, title, source, summary, category):
            logger.warning(f"Article validation failed for URL: {url}")
            return False

        # Check for duplicates - TR-010: Data Constraints
        if self.article_exists(url):
            logger.debug(f"Article already exists: {url}")
            return False

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-010: Store fetched_date in ISO 8601 format
                fetched_date = datetime.now().isoformat()

                # TR-010: Use parameterized query to prevent SQL injection
                cursor.execute('''
                    INSERT INTO articles (url, title, source, published_date,
                                        summary, category, fetched_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (url.strip(), title.strip(), source.strip(),
                      published_date, summary, category, fetched_date))

                logger.debug(f"Article added successfully: {title[:50]}...")
                return True

        except sqlite3.IntegrityError as e:
            # TR-030: Handle duplicate URL attempts gracefully
            logger.debug(f"Integrity error adding article (likely duplicate): {e}")
            return False
        except DatabaseError as e:
            logger.error(f"Failed to add article: {e}")
            return False

    def get_latest_articles(self, limit: int = 5) -> List[Dict]:
        """
        Get the latest articles from the database

        Requirements:
        - TR-022: !latest command implementation
        - TR-030: Exception Handling
        - TR-033: Input Validation

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        # TR-033: Validate limit parameter
        try:
            limit = int(limit)
            if limit <= 0:
                logger.warning(f"Invalid limit value: {limit}, using default 5")
                limit = 5
            if limit > 100:  # Prevent excessive queries
                logger.warning(f"Limit too large: {limit}, capping at 100")
                limit = 100
        except (ValueError, TypeError):
            logger.warning(f"Invalid limit type, using default 5")
            limit = 5

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-022: Query latest articles ordered by fetched_date
                cursor.execute('''
                    SELECT url, title, source, published_date, summary, category, fetched_date
                    FROM articles
                    ORDER BY fetched_date DESC
                    LIMIT ?
                ''', (limit,))

                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        'url': row[0],
                        'title': row[1],
                        'source': row[2],
                        'published_date': row[3],
                        'summary': row[4],
                        'category': row[5],
                        'fetched_date': row[6]
                    })

                logger.debug(f"Retrieved {len(articles)} latest articles")
                return articles

        except DatabaseError as e:
            logger.error(f"Failed to get latest articles: {e}")
            return []

    def get_unsent_articles(self) -> List[Dict]:
        """
        Get articles that haven't been sent in a digest yet

        Requirements:
        - TR-021: !digest command implementation
        - TR-030: Exception Handling

        Returns:
            List of unsent article dictionaries with IDs
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-021: Query unsent articles
                cursor.execute('''
                    SELECT id, url, title, source, published_date, summary, category, fetched_date
                    FROM articles
                    WHERE sent_in_digest = 0
                    ORDER BY fetched_date DESC
                ''')

                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'source': row[3],
                        'published_date': row[4],
                        'summary': row[5],
                        'category': row[6],
                        'fetched_date': row[7]
                    })

                logger.debug(f"Retrieved {len(articles)} unsent articles")
                return articles

        except DatabaseError as e:
            logger.error(f"Failed to get unsent articles: {e}")
            return []

    def mark_articles_sent(self, article_ids: List[int]):
        """
        Mark articles as sent in digest

        Requirements:
        - TR-010: Data Constraints (atomic update)
        - TR-021: Digest command implementation
        - TR-030: Exception Handling
        - TR-033: Input Validation

        Args:
            article_ids: List of article IDs to mark as sent
        """
        if not article_ids:
            logger.debug("No articles to mark as sent")
            return

        # TR-033: Validate article IDs
        try:
            article_ids = [int(aid) for aid in article_ids]
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid article IDs provided: {e}")
            return

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # TR-010: Use parameterized query to prevent SQL injection
                placeholders = ','.join('?' * len(article_ids))

                # TR-010: Atomic update operation
                cursor.execute(f'''
                    UPDATE articles
                    SET sent_in_digest = 1
                    WHERE id IN ({placeholders})
                ''', article_ids)

                rows_updated = cursor.rowcount
                logger.info(f"Marked {rows_updated} articles as sent")

        except DatabaseError as e:
            logger.error(f"Failed to mark articles as sent: {e}")
            raise

    def get_article_count(self) -> int:
        """
        Get total count of articles in database

        Requirements: TR-011: Data Retention monitoring

        Returns:
            int: Total number of articles
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM articles')
                count = cursor.fetchone()[0]
                return count
        except DatabaseError as e:
            logger.error(f"Failed to get article count: {e}")
            return 0
