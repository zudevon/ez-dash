"""
API Clients Module for Chad Loves AI
Handles interactions with NewsAPI, OpenWeatherMap, and Tiingo APIs.
"""

import os
import re
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_api_key(key_name: str) -> str:
    """
    Get API key from environment or Streamlit secrets.
    Supports both local development (.env) and Streamlit Cloud deployment.

    Args:
        key_name: Name of the API key environment variable

    Returns:
        The API key string
    """
    # First try to get from environment variables
    api_key = os.getenv(key_name)

    # If not found, try Streamlit secrets (for cloud deployment)
    if not api_key:
        try:
            # Import streamlit only when needed
            import streamlit as st
            # Access secrets from Streamlit Cloud
            api_key = st.secrets.get(key_name, '')
        except Exception:
            # Streamlit not available or secrets not configured
            pass

    # Return the API key (may be empty string if not found)
    return api_key or ''


class NewsAPIClient:
    """
    Client for fetching top news headlines from NewsAPI.
    Documentation: https://newsapi.org/docs/client-libraries/python
    """

    def __init__(self):
        """Initialize NewsAPI client with API key from environment."""
        # Get API key using helper function
        api_key = get_api_key('NEWS_API_KEY')
        # Initialize the NewsAPI client library
        self.client = NewsApiClient(api_key=api_key)

    def get_top_headlines(self, country: str = 'us',
                          page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch top news headlines from NewsAPI.

        Args:
            country: Two-letter country code (default: 'us')
            page_size: Number of articles to fetch (default: 10)

        Returns:
            List of article dictionaries containing headline, description, etc.
        """
        try:
            # Fetch top headlines using the client library
            response = self.client.get_top_headlines(
                country=country,
                page_size=page_size
            )

            # Check if the request was successful
            if response.get('status') == 'ok':
                # Return the list of articles
                return response.get('articles', [])
            else:
                # Return empty list on error
                print(f"NewsAPI Error: {response.get('message', 'Unknown error')}")
                return []

        except Exception as e:
            # Handle any exceptions during API call
            print(f"Error fetching news: {str(e)}")
            return []

    def get_news_by_date(self, date: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news articles for a specific date using the 'everything' endpoint.

        Args:
            date: Date string in YYYY-MM-DD format
            page_size: Number of articles to fetch (default: 10)

        Returns:
            List of article dictionaries containing headline, description, etc.
        """
        try:
            # Use get_everything for historical date queries
            response = self.client.get_everything(
                q='news',  # General search term
                from_param=date,
                to=date,
                language='en',
                sort_by='publishedAt',
                page_size=page_size
            )

            # Check if the request was successful
            if response.get('status') == 'ok':
                return response.get('articles', [])
            else:
                print(f"NewsAPI Error: {response.get('message', 'Unknown error')}")
                return []

        except Exception as e:
            print(f"Error fetching news for date {date}: {str(e)}")
            return []

    def extract_location_from_article(self, article: Dict[str, Any]) -> Optional[str]:
        """
        Extract location from article content using simple pattern matching.
        Checks for countries (mapped to capitals), international cities, and US cities.

        Args:
            article: Article dictionary from NewsAPI

        Returns:
            Location string if found (city name for weather API), None otherwise
        """
        # Combine title and description for location extraction
        text = f"{article.get('title', '')} {article.get('description', '')}"
        text_lower = text.lower()

        # Countries mapped to their capital cities for weather API
        country_to_capital = {
            'France': 'Paris', 'French': 'Paris',
            'Germany': 'Berlin', 'German': 'Berlin',
            'Japan': 'Tokyo', 'Japanese': 'Tokyo',
            'China': 'Beijing', 'Chinese': 'Beijing',
            'United Kingdom': 'London', 'UK': 'London', 'Britain': 'London', 'British': 'London', 'England': 'London',
            'Italy': 'Rome', 'Italian': 'Rome',
            'Spain': 'Madrid', 'Spanish': 'Madrid',
            'Russia': 'Moscow', 'Russian': 'Moscow',
            'Australia': 'Sydney', 'Australian': 'Sydney',
            'Canada': 'Toronto', 'Canadian': 'Toronto',
            'India': 'Mumbai', 'Indian': 'Mumbai',
            'Brazil': 'Brasilia', 'Brazilian': 'Brasilia',
            'Mexico': 'Mexico City', 'Mexican': 'Mexico City',
            'South Korea': 'Seoul', 'Korean': 'Seoul',
            'Netherlands': 'Amsterdam', 'Dutch': 'Amsterdam',
            'Switzerland': 'Zurich', 'Swiss': 'Zurich',
            'Sweden': 'Stockholm', 'Swedish': 'Stockholm',
            'Norway': 'Oslo', 'Norwegian': 'Oslo',
            'Poland': 'Warsaw', 'Polish': 'Warsaw',
            'Ukraine': 'Kyiv', 'Ukrainian': 'Kyiv',
            'Israel': 'Tel Aviv', 'Israeli': 'Tel Aviv',
            'Saudi Arabia': 'Riyadh', 'Saudi': 'Riyadh',
            'UAE': 'Dubai', 'United Arab Emirates': 'Dubai',
            'Singapore': 'Singapore',
            'Thailand': 'Bangkok', 'Thai': 'Bangkok',
            'Vietnam': 'Hanoi', 'Vietnamese': 'Hanoi',
            'Indonesia': 'Jakarta', 'Indonesian': 'Jakarta',
            'Philippines': 'Manila', 'Filipino': 'Manila',
            'Taiwan': 'Taipei', 'Taiwanese': 'Taipei',
            'Argentina': 'Buenos Aires', 'Argentine': 'Buenos Aires',
            'Chile': 'Santiago', 'Chilean': 'Santiago',
            'Egypt': 'Cairo', 'Egyptian': 'Cairo',
            'South Africa': 'Johannesburg', 'South African': 'Johannesburg',
            'Nigeria': 'Lagos', 'Nigerian': 'Lagos',
            'Turkey': 'Istanbul', 'Turkish': 'Istanbul',
            'Greece': 'Athens', 'Greek': 'Athens',
            'Portugal': 'Lisbon', 'Portuguese': 'Lisbon',
            'Ireland': 'Dublin', 'Irish': 'Dublin',
            'Austria': 'Vienna', 'Austrian': 'Vienna',
            'Belgium': 'Brussels', 'Belgian': 'Brussels',
            'Denmark': 'Copenhagen', 'Danish': 'Copenhagen',
            'Finland': 'Helsinki', 'Finnish': 'Helsinki',
            'Czech Republic': 'Prague', 'Czech': 'Prague',
            'Hungary': 'Budapest', 'Hungarian': 'Budapest',
            'New Zealand': 'Auckland',
        }

        # Check for country mentions first (map to capital city)
        for country, capital in country_to_capital.items():
            if country.lower() in text_lower:
                return capital

        # International cities (major world cities)
        international_cities = [
            'London', 'Paris', 'Berlin', 'Tokyo', 'Sydney', 'Toronto', 'Mumbai',
            'Beijing', 'Dubai', 'Singapore', 'Moscow', 'Rome', 'Madrid',
            'Amsterdam', 'Brussels', 'Vienna', 'Zurich', 'Hong Kong', 'Seoul',
            'Bangkok', 'Shanghai', 'Osaka', 'Melbourne', 'Vancouver', 'Montreal',
            'Dublin', 'Edinburgh', 'Manchester', 'Munich', 'Frankfurt', 'Milan',
            'Barcelona', 'Lisbon', 'Prague', 'Warsaw', 'Budapest', 'Stockholm',
            'Oslo', 'Copenhagen', 'Helsinki', 'Athens', 'Istanbul', 'Tel Aviv',
            'Cairo', 'Lagos', 'Johannesburg', 'Cape Town', 'Nairobi', 'Casablanca',
            'Buenos Aires', 'Sao Paulo', 'Rio de Janeiro', 'Lima', 'Bogota',
            'Santiago', 'Mexico City', 'Havana', 'San Juan', 'Jakarta', 'Manila',
            'Hanoi', 'Ho Chi Minh', 'Kuala Lumpur', 'Taipei', 'Auckland', 'Wellington'
        ]

        # Check international cities
        for city in international_cities:
            if city.lower() in text_lower:
                return city

        # US cities (major metropolitan areas)
        us_cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
            'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte',
            'Seattle', 'Denver', 'Washington', 'Boston', 'Nashville',
            'Detroit', 'Portland', 'Las Vegas', 'Memphis', 'Louisville',
            'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno',
            'Sacramento', 'Kansas City', 'Atlanta', 'Miami', 'Oakland',
            'Minneapolis', 'Cleveland', 'Tampa', 'St. Louis', 'Pittsburgh',
            'San Francisco', 'New Orleans', 'Honolulu', 'Anchorage', 'Salt Lake City',
            'Raleigh', 'Richmond', 'Hartford', 'Providence', 'Buffalo'
        ]

        # Check US cities
        for city in us_cities:
            if city.lower() in text_lower:
                return city

        # Return None if no location found
        return None

    def extract_companies_from_article(self, article: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract company names and their stock tickers from article.

        Args:
            article: Article dictionary from NewsAPI

        Returns:
            List of tuples containing (ticker, company_name)
        """
        # Combine title and description for company extraction
        text = f"{article.get('title', '')} {article.get('description', '')}"

        # Dictionary mapping company names to stock tickers
        # These are commonly mentioned tech/major companies
        company_tickers = {
            'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Google': 'GOOGL',
            'Amazon': 'AMZN', 'Meta': 'META', 'Facebook': 'META',
            'Tesla': 'TSLA', 'Netflix': 'NFLX', 'Nvidia': 'NVDA',
            'AMD': 'AMD', 'Intel': 'INTC', 'IBM': 'IBM',
            'Walmart': 'WMT', 'Disney': 'DIS', 'Nike': 'NKE',
            'Coca-Cola': 'KO', 'Pepsi': 'PEP', 'McDonald': 'MCD',
            'Starbucks': 'SBUX', 'Boeing': 'BA', 'Ford': 'F',
            'General Motors': 'GM', 'Exxon': 'XOM', 'Chevron': 'CVX',
            'JPMorgan': 'JPM', 'Bank of America': 'BAC', 'Goldman': 'GS',
            'Visa': 'V', 'Mastercard': 'MA', 'PayPal': 'PYPL',
            'Uber': 'UBER', 'Lyft': 'LYFT', 'Airbnb': 'ABNB',
            'Twitter': 'X', 'Snap': 'SNAP', 'Pinterest': 'PINS',
            'Salesforce': 'CRM', 'Adobe': 'ADBE', 'Oracle': 'ORCL',
            'Cisco': 'CSCO', 'Qualcomm': 'QCOM', 'Broadcom': 'AVGO'
        }

        # List to store found companies
        found_companies = []

        # Search for each company name in the text
        for company, ticker in company_tickers.items():
            # Use case-insensitive search
            if company.lower() in text.lower():
                # Add tuple of (ticker, company) to results
                found_companies.append((ticker, company))

        # Return list of found companies
        return found_companies


class WeatherAPIClient:
    """
    Client for fetching weather data from OpenWeatherMap API.
    Documentation: https://openweathermap.org/current
    """

    def __init__(self):
        """Initialize Weather API client with API key from environment."""
        # Get API key using helper function
        self.api_key = get_api_key('WEATHER_API_KEY')
        # Base URL for OpenWeatherMap API
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather_by_city(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for a specific city.

        Args:
            city: Name of the city to get weather for

        Returns:
            Dictionary containing weather data or None on error
        """
        try:
            # Build request parameters with imperial units (Fahrenheit)
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'imperial'  # Use Fahrenheit for US users
            }

            # Make GET request to OpenWeatherMap API
            response = requests.get(self.base_url, params=params)

            # Check if request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Extract and return relevant weather data
                return {
                    'location': data.get('name', city),
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Log error and return None
                print(f"Weather API Error: {response.status_code}")
                return None

        except Exception as e:
            # Handle any exceptions during API call
            print(f"Error fetching weather: {str(e)}")
            return None


class StockAPIClient:
    """
    Client for fetching stock prices from Tiingo API.
    Documentation: https://api.tiingo.com/documentation/general/overview
    """

    def __init__(self):
        """Initialize Tiingo API client with API key from environment."""
        # Get API key using helper function
        self.api_key = get_api_key('TIINGO_API_KEY')
        # Base URL for Tiingo daily prices endpoint
        self.base_url = "https://api.tiingo.com/tiingo/daily"

    def get_stock_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest stock price for a given ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dictionary containing stock price data or None on error
        """
        try:
            # Build the API URL with ticker and token
            url = f"{self.base_url}/{ticker}/prices?token={self.api_key}"

            # Set headers for the request
            headers = {
                'Content-Type': 'application/json'
            }

            # Make GET request to Tiingo API
            response = requests.get(url, headers=headers)

            # Check if request was successful
            if response.status_code == 200:
                # Parse the JSON response (returns a list)
                data = response.json()

                # Check if data is not empty
                if data and len(data) > 0:
                    # Get the latest price data (first item)
                    latest = data[0]

                    # Return formatted stock data
                    return {
                        'ticker': ticker.upper(),
                        'price': latest.get('close', latest.get('adjClose', 0)),
                        'date': latest.get('date', datetime.now().isoformat())
                    }

            # Return None if no data found
            print(f"Stock API Error for {ticker}: {response.status_code}")
            return None

        except Exception as e:
            # Handle any exceptions during API call
            print(f"Error fetching stock {ticker}: {str(e)}")
            return None

    def get_sp500_price(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the S&P 500 index price using SPY ETF as proxy.

        Returns:
            Dictionary containing S&P 500 price data or None on error
        """
        # SPY is the SPDR S&P 500 ETF that tracks the index
        result = self.get_stock_price('SPY')

        # Update the ticker name for display
        if result:
            result['ticker'] = 'SPY'
            result['company_name'] = 'S&P 500 ETF'

        # Return the S&P 500 proxy data
        return result


def fetch_all_data(date: Optional[str] = None) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Fetch all data from APIs: news, weather, and stocks.
    This is the main function to populate the dashboard.

    Args:
        date: Optional date string in YYYY-MM-DD format. If provided, fetches
              news for that specific date. If None, fetches today's headlines.

    Returns:
        Tuple of (news_list, weather_list, stocks_list)
    """
    # Initialize all API clients
    news_client = NewsAPIClient()
    weather_client = WeatherAPIClient()
    stock_client = StockAPIClient()

    # Fetch news based on date parameter
    today = datetime.now().strftime('%Y-%m-%d')
    if date and date != today:
        # Fetch historical news for the specified date
        articles = news_client.get_news_by_date(date, page_size=5)
    else:
        # Fetch today's top headlines
        articles = news_client.get_top_headlines(page_size=5)

    # Lists to store processed data
    news_data = []
    weather_data = []
    stock_data = []

    # Track locations and companies we've already fetched
    fetched_locations = set()
    fetched_tickers = set()

    # Process each news article
    for article in articles:
        # Extract location from article text
        location = news_client.extract_location_from_article(article)

        # Build news data dictionary
        news_item = {
            'headline': article.get('title', 'No Title'),
            'description': article.get('description', ''),
            'url': article.get('url', ''),
            'source': article.get('source', {}).get('name', 'Unknown'),
            'location': location,
            'published_date': article.get('publishedAt', datetime.now().isoformat())
        }

        # Add to news data list
        news_data.append(news_item)

        # Fetch weather for the location if not already fetched
        if location and location not in fetched_locations:
            # Get weather data for this location
            weather = weather_client.get_weather_by_city(location)
            if weather:
                # Add to weather data list
                weather_data.append(weather)
                # Mark location as fetched
                fetched_locations.add(location)

        # Extract companies mentioned in the article
        companies = news_client.extract_companies_from_article(article)

        # Fetch stock prices for each company
        for ticker, company_name in companies:
            # Skip if already fetched this ticker
            if ticker not in fetched_tickers:
                # Get stock price for this ticker
                stock = stock_client.get_stock_price(ticker)
                if stock:
                    # Add company name to stock data
                    stock['company_name'] = company_name
                    # Add to stock data list
                    stock_data.append(stock)
                    # Mark ticker as fetched
                    fetched_tickers.add(ticker)

    # If no companies found, fetch S&P 500 as default
    if not stock_data:
        # Get S&P 500 ETF price as fallback
        sp500 = stock_client.get_sp500_price()
        if sp500:
            stock_data.append(sp500)

    # Return all collected data
    return news_data, weather_data, stock_data


def refresh_stock_prices(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Refresh stock prices for a list of tickers.
    Used for the 5-second auto-refresh feature.

    Args:
        tickers: List of stock ticker symbols to refresh

    Returns:
        List of dictionaries containing updated stock prices
    """
    # Initialize stock API client
    stock_client = StockAPIClient()

    # List to store updated prices
    updated_prices = []

    # Fetch price for each ticker
    for ticker in tickers:
        # Get the latest price
        stock = stock_client.get_stock_price(ticker)
        if stock:
            # Add to results list
            updated_prices.append(stock)

    # Return all updated prices
    return updated_prices
