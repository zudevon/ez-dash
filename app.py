"""
Chad Loves AI - News Dashboard Application
Main Streamlit application that displays news, weather, and stock data.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import utility modules for database, API, and caching
from utils.database import DatabaseManager
from utils.api_clients import fetch_all_data, refresh_stock_prices
from utils.cache import NewsCache


# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Chad Loves AI - News Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables.
    Session state persists across reruns within a session.
    """
    # Initialize database manager in session state
    if 'db' not in st.session_state:
        # Create in-memory SQLite database
        st.session_state.db = DatabaseManager()

    # Initialize news cache in session state
    if 'cache' not in st.session_state:
        # Create cache with 10-day retention
        st.session_state.cache = NewsCache()

    # Track if data has been loaded
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # Track the currently loaded date
    if 'loaded_date' not in st.session_state:
        st.session_state.loaded_date = None

    # Store current stock tickers for refresh
    if 'stock_tickers' not in st.session_state:
        st.session_state.stock_tickers = []

    # Store the last refresh timestamp
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()

    # Track auto-refresh state
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True


def load_data(selected_date: str) -> None:
    """
    Load data from APIs (or cache) and store in database.
    Shows a progress indicator while loading.

    Args:
        selected_date: Date string in YYYY-MM-DD format to fetch news for
    """
    # Check cache first for this date
    cached_news = st.session_state.cache.get(selected_date)

    if cached_news:
        # Use cached news data
        news_data = cached_news
        # Still need to fetch weather and stocks fresh
        with st.spinner(f"Loading cached news for {selected_date}..."):
            # Fetch weather and stocks (these are always current)
            from utils.api_clients import WeatherAPIClient, StockAPIClient, NewsAPIClient
            news_client = NewsAPIClient()
            weather_client = WeatherAPIClient()
            stock_client = StockAPIClient()

            weather_data = []
            stock_data = []
            fetched_locations = set()
            fetched_tickers = set()

            # Process cached news for weather and stocks
            for news in news_data:
                location = news.get('location')
                if location and location not in fetched_locations:
                    weather = weather_client.get_weather_by_city(location)
                    if weather:
                        weather_data.append(weather)
                        fetched_locations.add(location)

                # Re-extract companies from headline/description
                article = {'title': news['headline'], 'description': news['description']}
                companies = news_client.extract_companies_from_article(article)
                for ticker, company_name in companies:
                    if ticker not in fetched_tickers:
                        stock = stock_client.get_stock_price(ticker)
                        if stock:
                            stock['company_name'] = company_name
                            stock_data.append(stock)
                            fetched_tickers.add(ticker)

            # Fallback to S&P 500 if no stocks found
            if not stock_data:
                sp500 = stock_client.get_sp500_price()
                if sp500:
                    stock_data.append(sp500)
    else:
        # Fetch fresh data from APIs
        with st.spinner(f"Fetching news for {selected_date}..."):
            news_data, weather_data, stock_data = fetch_all_data(date=selected_date)
            # Cache the news data for future use
            st.session_state.cache.set(selected_date, news_data)

    # Clear existing data from database
    st.session_state.db.clear_all_data()

    # Insert news data into database
    for news in news_data:
        st.session_state.db.insert_news(
            headline=news['headline'],
            description=news['description'],
            url=news['url'],
            source=news['source'],
            location=news['location'],
            published_date=news['published_date']
        )

    # Insert weather data into database
    for weather in weather_data:
        st.session_state.db.insert_weather(
            location=weather['location'],
            temperature=weather['temperature'],
            feels_like=weather['feels_like'],
            humidity=weather['humidity'],
            description=weather['description'],
            icon=weather['icon'],
            date=weather['date']
        )

    # Insert stock data and track tickers
    tickers = []
    for stock in stock_data:
        st.session_state.db.insert_stock(
            ticker=stock['ticker'],
            company_name=stock.get('company_name', stock['ticker']),
            price=stock['price'],
            date=stock['date']
        )
        tickers.append(stock['ticker'])

    # Store tickers in session state for refresh
    st.session_state.stock_tickers = tickers

    # Mark data as loaded and track the loaded date
    st.session_state.data_loaded = True
    st.session_state.loaded_date = selected_date

    # Update refresh timestamp
    st.session_state.last_refresh = datetime.now()


def display_header() -> None:
    """Display the application header with title and description."""
    # Create header with emoji and title
    st.title("📰 Chad Loves AI")
    # Add subtitle with description
    st.markdown("*Your AI-powered news dashboard with weather and stock insights*")
    # Add horizontal divider
    st.divider()


def display_sidebar() -> str:
    """
    Display the sidebar with date filter and controls.

    Returns:
        Selected date string in YYYY-MM-DD format
    """
    # Create sidebar header
    st.sidebar.header("📅 Filter Options")

    # Generate list of dates for the past week
    # Using list comprehension for date generation
    date_options = [
        (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(7)
    ]

    # Create date selector dropdown
    selected_date = st.sidebar.selectbox(
        "Select Date",
        options=date_options,
        index=0,  # Default to today
        help="Filter news by date (past 7 days)"
    )

    # Add refresh button
    if st.sidebar.button("🔄 Refresh All Data", use_container_width=True):
        # Reset data loaded flag to trigger reload
        st.session_state.data_loaded = False
        # Rerun the app to reload data
        st.rerun()

    # Add auto-refresh toggle
    st.sidebar.divider()
    st.session_state.auto_refresh = st.sidebar.checkbox(
        "Auto-refresh stocks (60s)",
        value=st.session_state.auto_refresh,
        help="Automatically refresh stock prices every 60 seconds"
    )

    # Display last refresh time
    st.sidebar.caption(
        f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}"
    )

    # Add info section
    st.sidebar.divider()
    st.sidebar.info(
        "💡 **About:** Chad Loves AI aggregates news with related "
        "weather and stock market data for a comprehensive view."
    )

    # Return the selected date
    return selected_date


def display_news_section() -> None:
    """Display the news headlines section."""
    # Create section header
    st.header("📰 Top News Headlines")

    # Get all news from database
    news_items = st.session_state.db.get_all_news()

    # Check if we have news data
    if not news_items:
        # Display warning if no news found
        st.warning("No news articles found. Click 'Refresh All Data' to load.")
        return

    # Display each news article in a card-like format
    # Limit to 5 articles as per requirements
    for i, news in enumerate(news_items[:5]):
        # Create an expander for each news item
        with st.expander(f"**{news['headline']}**", expanded=(i < 3)):
            # Display news metadata in columns
            col1, col2, col3 = st.columns(3)

            # Source column
            with col1:
                st.caption(f"📍 Source: {news['source']}")

            # Location column (if available)
            with col2:
                if news['location']:
                    st.caption(f"🌍 Location: {news['location']}")

            # Date column
            with col3:
                # Format the date for display
                pub_date = news['published_date'][:10] if news['published_date'] else 'N/A'
                st.caption(f"📅 Date: {pub_date}")

            # Display description
            if news['description']:
                st.write(news['description'])

            # Display link to full article
            if news['url']:
                st.markdown(f"[Read full article →]({news['url']})")


def display_weather_section() -> None:
    """Display the weather data section."""
    # Create section header
    st.header("🌤️ Weather Updates")

    # Query weather data from database
    cursor = st.session_state.db.connection.cursor()
    cursor.execute('SELECT * FROM weather')
    weather_items = [dict(row) for row in cursor.fetchall()]

    # Check if we have weather data
    if not weather_items:
        # Display info message if no weather data
        st.info("No weather data available for news locations.")
        return

    # Create columns for weather cards
    # Using min to handle fewer than 3 items
    cols = st.columns(min(len(weather_items), 3))

    # Display each weather item in a column
    for i, weather in enumerate(weather_items[:3]):
        with cols[i % 3]:
            # Create a metric card for weather
            st.metric(
                label=f"🌡️ {weather['location']}",
                value=f"{weather['temperature']:.1f}°F",
                delta=f"Feels like {weather['feels_like']:.1f}°F"
            )
            # Display weather description
            st.caption(f"☁️ {weather['description'].title()}")
            # Display humidity
            st.caption(f"💧 Humidity: {weather['humidity']}%")


def display_stocks_section() -> None:
    """
    Display the stock prices section with auto-refresh.
    Stock prices update every 5 seconds when enabled.
    """
    # Custom CSS to reduce stock price font size
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create section header with refresh indicator
    st.header("📈 Stock Prices")

    # Get all stocks from database
    stocks = st.session_state.db.get_all_stocks()

    # Check if we have stock data
    if not stocks:
        st.info("No stock data available. Using S&P 500 as default.")
        return

    # Create columns for stock cards
    # Limit to 4 columns for better display
    num_cols = min(len(stocks), 4)
    cols = st.columns(num_cols)

    # Display each stock in a column
    for i, stock in enumerate(stocks):
        with cols[i % num_cols]:
            # Create metric card for stock
            st.metric(
                label=f"💹 {stock['ticker']}",
                value=f"${stock['price']:.2f}",
                delta=None  # Could add price change if API provides it
            )
            # Display company name
            if stock.get('company_name'):
                st.caption(stock['company_name'])

    # Show refresh button for manual stock update
    if st.button("🔄 Refresh Stock Prices", key="refresh_stocks"):
        refresh_stocks_now()
        st.rerun()


def refresh_stocks_now() -> None:
    """
    Refresh stock prices immediately.
    Called by button or auto-refresh.
    """
    # Check if we have tickers to refresh
    if not st.session_state.stock_tickers:
        return

    # Fetch updated stock prices
    updated_stocks = refresh_stock_prices(st.session_state.stock_tickers)

    # Update prices in database
    for stock in updated_stocks:
        st.session_state.db.update_stock_price(
            ticker=stock['ticker'],
            price=stock['price'],
            date=stock['date']
        )

    # Update last refresh timestamp
    st.session_state.last_refresh = datetime.now()


def main() -> None:
    """
    Main application entry point.
    Orchestrates the dashboard layout and data flow.
    """
    # Initialize session state variables
    initialize_session_state()

    # Display application header
    display_header()

    # Display sidebar and get selected date
    selected_date = display_sidebar()

    # Load data if not already loaded or if date changed
    if not st.session_state.data_loaded or st.session_state.loaded_date != selected_date:
        load_data(selected_date)

    # Create main content layout with columns
    # Left column (wider) for news, right column for weather/stocks
    news_col, data_col = st.columns([2, 1])

    # Display news in left column
    with news_col:
        display_news_section()

    # Display weather and stocks in right column
    with data_col:
        display_weather_section()
        st.divider()
        display_stocks_section()

    # Auto-refresh stocks if enabled
    # Using st.empty with auto_refresh to trigger periodic updates
    if st.session_state.auto_refresh and st.session_state.stock_tickers:
        # Check if enough time has passed (60 seconds to avoid API rate limits)
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()

        # Only auto-refresh if 60+ seconds have passed
        if time_since_refresh >= 60:
            refresh_stocks_now()
            # Use rerun to update the display
            st.rerun()


# Entry point for the application
if __name__ == "__main__":
    main()
