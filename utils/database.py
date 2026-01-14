"""
Database Module for Chad Loves AI
Handles SQLite in-memory database operations for news, weather, and stock data.
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any


class DatabaseManager:
    """
    Manages SQLite in-memory database connections and operations.
    Stores news headlines, weather data, and stock prices.
    """

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize database connection and create tables.

        Args:
            db_path: Path to database file or ':memory:' for in-memory db
        """
        # Create connection to SQLite database
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        # Enable dictionary-style row access
        self.connection.row_factory = sqlite3.Row
        # Create database tables on initialization
        self._create_tables()

    def _create_tables(self) -> None:
        """
        Create the required database tables for news, weather, and stocks.
        Uses IF NOT EXISTS to prevent errors on reconnection.
        """
        cursor = self.connection.cursor()

        # Create News table to store headlines and metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT NOT NULL,
                description TEXT,
                url TEXT,
                source TEXT,
                location TEXT,
                published_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Weather table to store temperature data by location
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL,
                feels_like REAL,
                humidity INTEGER,
                description TEXT,
                icon TEXT,
                date TEXT,
                news_id INTEGER,
                FOREIGN KEY (news_id) REFERENCES news (id)
            )
        ''')

        # Create Stocks table to store company stock prices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                company_name TEXT,
                price REAL,
                date TEXT,
                news_id INTEGER,
                FOREIGN KEY (news_id) REFERENCES news (id)
            )
        ''')

        # Commit the table creation
        self.connection.commit()

    def insert_news(self, headline: str, description: str, url: str,
                    source: str, location: Optional[str],
                    published_date: str) -> int:
        """
        Insert a news article into the database.

        Args:
            headline: Article headline/title
            description: Brief description of the article
            url: Link to the full article
            source: News source name
            location: Location mentioned in the article (if any)
            published_date: Publication date of the article

        Returns:
            The ID of the inserted news record
        """
        cursor = self.connection.cursor()

        # Insert news data into the news table
        cursor.execute('''
            INSERT INTO news (headline, description, url, source, location, published_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (headline, description, url, source, location, published_date))

        # Commit and return the new record ID
        self.connection.commit()
        return cursor.lastrowid

    def insert_weather(self, location: str, temperature: float,
                       feels_like: float, humidity: int, description: str,
                       icon: str, date: str, news_id: Optional[int] = None) -> int:
        """
        Insert weather data into the database.

        Args:
            location: City/location name
            temperature: Current temperature in Fahrenheit
            feels_like: Feels-like temperature in Fahrenheit
            humidity: Humidity percentage
            description: Weather description (e.g., 'clear sky')
            icon: Weather icon code from API
            date: Date of the weather data
            news_id: Related news article ID (optional)

        Returns:
            The ID of the inserted weather record
        """
        cursor = self.connection.cursor()

        # Insert weather data linked to news if provided
        cursor.execute('''
            INSERT INTO weather (location, temperature, feels_like, humidity,
                               description, icon, date, news_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location, temperature, feels_like, humidity, description,
              icon, date, news_id))

        # Commit and return the new record ID
        self.connection.commit()
        return cursor.lastrowid

    def insert_stock(self, ticker: str, company_name: str, price: float,
                     date: str, news_id: Optional[int] = None) -> int:
        """
        Insert stock price data into the database.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            company_name: Full company name
            price: Current stock price
            date: Date of the price data
            news_id: Related news article ID (optional)

        Returns:
            The ID of the inserted stock record
        """
        cursor = self.connection.cursor()

        # Insert stock data linked to news if provided
        cursor.execute('''
            INSERT INTO stocks (ticker, company_name, price, date, news_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, company_name, price, date, news_id))

        # Commit and return the new record ID
        self.connection.commit()
        return cursor.lastrowid

    def get_all_news(self) -> List[Dict[str, Any]]:
        """
        Retrieve all news articles from the database.

        Returns:
            List of dictionaries containing news data
        """
        cursor = self.connection.cursor()

        # Select all news ordered by published date descending
        cursor.execute('''
            SELECT * FROM news ORDER BY published_date DESC
        ''')

        # Convert rows to dictionaries using list comprehension
        return [dict(row) for row in cursor.fetchall()]

    def get_news_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Retrieve news articles for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of dictionaries containing news data for that date
        """
        cursor = self.connection.cursor()

        # Use LIKE to match the date portion of published_date
        cursor.execute('''
            SELECT * FROM news
            WHERE published_date LIKE ?
            ORDER BY published_date DESC
        ''', (f"{date}%",))

        # Convert rows to dictionaries
        return [dict(row) for row in cursor.fetchall()]

    def get_weather_for_news(self, news_id: int) -> Optional[Dict[str, Any]]:
        """
        Get weather data associated with a specific news article.

        Args:
            news_id: The ID of the news article

        Returns:
            Dictionary containing weather data or None if not found
        """
        cursor = self.connection.cursor()

        # Select weather data for the given news ID
        cursor.execute('''
            SELECT * FROM weather WHERE news_id = ?
        ''', (news_id,))

        # Return the first result as dict or None
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_stocks_for_news(self, news_id: int) -> List[Dict[str, Any]]:
        """
        Get stock data associated with a specific news article.

        Args:
            news_id: The ID of the news article

        Returns:
            List of dictionaries containing stock data
        """
        cursor = self.connection.cursor()

        # Select all stocks linked to the given news ID
        cursor.execute('''
            SELECT * FROM stocks WHERE news_id = ?
        ''', (news_id,))

        # Convert rows to dictionaries
        return [dict(row) for row in cursor.fetchall()]

    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """
        Retrieve all unique stock tickers and their latest prices.

        Returns:
            List of dictionaries containing stock data
        """
        cursor = self.connection.cursor()

        # Get distinct tickers with their most recent price
        # Order by id to preserve first-appearance order from news articles
        cursor.execute('''
            SELECT DISTINCT ticker, company_name, price, date
            FROM stocks
            ORDER BY id
        ''')

        # Convert rows to dictionaries
        return [dict(row) for row in cursor.fetchall()]

    def update_stock_price(self, ticker: str, price: float, date: str) -> None:
        """
        Update the price for a specific stock ticker.

        Args:
            ticker: Stock ticker symbol
            price: New stock price
            date: Date of the price update
        """
        cursor = self.connection.cursor()

        # Update all records with the matching ticker
        cursor.execute('''
            UPDATE stocks SET price = ?, date = ? WHERE ticker = ?
        ''', (price, date, ticker))

        # Commit the update
        self.connection.commit()

    def clear_all_data(self) -> None:
        """
        Clear all data from all tables.
        Useful for refreshing data or testing.
        """
        cursor = self.connection.cursor()

        # Delete all records from each table
        cursor.execute('DELETE FROM stocks')
        cursor.execute('DELETE FROM weather')
        cursor.execute('DELETE FROM news')

        # Commit the deletions
        self.connection.commit()

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
