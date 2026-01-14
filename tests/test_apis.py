"""
API Tests for Chad Loves AI
Tests each API client and logs responses to verify data quality.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging to show detailed API responses
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API clients from utils
from utils.api_clients import (
    NewsAPIClient,
    WeatherAPIClient,
    StockAPIClient,
    fetch_all_data
)


def log_response(api_name: str, response: Any) -> None:
    """
    Log API response in a readable format.

    Args:
        api_name: Name of the API being tested
        response: The response data to log
    """
    # Create separator for readability
    separator = "=" * 60
    logger.info(f"\n{separator}")
    logger.info(f"API: {api_name}")
    logger.info(f"{separator}")

    # Pretty print the response as JSON
    if response:
        logger.info(f"Response:\n{json.dumps(response, indent=2, default=str)}")
    else:
        logger.warning(f"No response received from {api_name}")


def test_news_api() -> bool:
    """
    Test NewsAPI client and log response.

    Returns:
        True if test passed, False otherwise
    """
    logger.info("\n>>> Testing NewsAPI Client <<<")

    try:
        # Initialize the NewsAPI client
        client = NewsAPIClient()

        # Fetch top 5 headlines (reduced from 10)
        articles = client.get_top_headlines(country='us', page_size=5)

        # Check if we got articles
        if not articles:
            logger.error("NewsAPI returned no articles")
            return False

        # Log the number of articles received
        logger.info(f"Received {len(articles)} articles from NewsAPI")

        # Log each article's key fields
        for i, article in enumerate(articles):
            article_summary = {
                'index': i + 1,
                'title': article.get('title', 'N/A'),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'publishedAt': article.get('publishedAt', 'N/A'),
                'description': article.get('description', 'N/A')[:100] + '...' if article.get('description') else 'N/A',
                'url': article.get('url', 'N/A')
            }
            log_response(f"NewsAPI Article {i + 1}", article_summary)

        # Test location extraction
        logger.info("\n--- Testing Location Extraction ---")
        for article in articles[:3]:
            location = client.extract_location_from_article(article)
            logger.info(f"Article: {article.get('title', 'N/A')[:50]}...")
            logger.info(f"Extracted Location: {location or 'None found'}")

        # Test company extraction
        logger.info("\n--- Testing Company Extraction ---")
        for article in articles[:3]:
            companies = client.extract_companies_from_article(article)
            logger.info(f"Article: {article.get('title', 'N/A')[:50]}...")
            logger.info(f"Extracted Companies: {companies or 'None found'}")

        logger.info("\n✅ NewsAPI Test PASSED")
        return True

    except Exception as e:
        logger.error(f"NewsAPI Test FAILED: {str(e)}")
        return False


def test_weather_api() -> bool:
    """
    Test OpenWeatherMap API client and log response.

    Returns:
        True if test passed, False otherwise
    """
    logger.info("\n>>> Testing Weather API Client <<<")

    # Test cities to query weather for
    test_cities = ['New York', 'Los Angeles', 'Chicago', 'Miami', 'Seattle']

    try:
        # Initialize the Weather API client
        client = WeatherAPIClient()

        # Track successful and failed requests
        successful = 0
        failed = 0

        # Test each city
        for city in test_cities:
            logger.info(f"\n--- Fetching weather for: {city} ---")

            # Get weather data
            weather = client.get_weather_by_city(city)

            if weather:
                # Log the weather response
                log_response(f"Weather for {city}", weather)

                # Verify required fields exist
                required_fields = ['location', 'temperature', 'feels_like', 'humidity', 'description']
                missing_fields = [f for f in required_fields if f not in weather]

                if missing_fields:
                    logger.warning(f"Missing fields in response: {missing_fields}")
                else:
                    logger.info(f"✓ All required fields present for {city}")
                    successful += 1
            else:
                logger.error(f"✗ Failed to get weather for {city}")
                failed += 1

        # Log summary
        logger.info(f"\n--- Weather API Summary ---")
        logger.info(f"Successful: {successful}/{len(test_cities)}")
        logger.info(f"Failed: {failed}/{len(test_cities)}")

        if successful >= 3:
            logger.info("\n✅ Weather API Test PASSED")
            return True
        else:
            logger.error("\n❌ Weather API Test FAILED (too many failures)")
            return False

    except Exception as e:
        logger.error(f"Weather API Test FAILED: {str(e)}")
        return False


def test_stock_api() -> bool:
    """
    Test Tiingo Stock API client and log response.

    Returns:
        True if test passed, False otherwise
    """
    logger.info("\n>>> Testing Tiingo Stock API Client <<<")

    # Test tickers to query
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'SPY']

    try:
        # Initialize the Stock API client
        client = StockAPIClient()

        # Track successful and failed requests
        successful = 0
        failed = 0

        # Test each ticker
        for ticker in test_tickers:
            logger.info(f"\n--- Fetching stock price for: {ticker} ---")

            # Get stock price
            stock = client.get_stock_price(ticker)

            if stock:
                # Log the stock response
                log_response(f"Stock Price for {ticker}", stock)

                # Verify required fields exist
                required_fields = ['ticker', 'price', 'date']
                missing_fields = [f for f in required_fields if f not in stock]

                if missing_fields:
                    logger.warning(f"Missing fields in response: {missing_fields}")
                else:
                    logger.info(f"✓ All required fields present for {ticker}")
                    successful += 1
            else:
                logger.error(f"✗ Failed to get stock price for {ticker}")
                failed += 1

        # Test S&P 500 proxy function
        logger.info("\n--- Testing S&P 500 Proxy (SPY) ---")
        sp500 = client.get_sp500_price()
        if sp500:
            log_response("S&P 500 ETF (SPY)", sp500)
            logger.info("✓ S&P 500 proxy function works")
        else:
            logger.warning("✗ S&P 500 proxy function failed")

        # Log summary
        logger.info(f"\n--- Stock API Summary ---")
        logger.info(f"Successful: {successful}/{len(test_tickers)}")
        logger.info(f"Failed: {failed}/{len(test_tickers)}")

        if successful >= 3:
            logger.info("\n✅ Stock API Test PASSED")
            return True
        else:
            logger.error("\n❌ Stock API Test FAILED (too many failures)")
            return False

    except Exception as e:
        logger.error(f"Stock API Test FAILED: {str(e)}")
        return False


def test_fetch_all_data() -> bool:
    """
    Test the combined fetch_all_data function.

    Returns:
        True if test passed, False otherwise
    """
    logger.info("\n>>> Testing Combined fetch_all_data Function <<<")

    try:
        # Fetch all data
        news_data, weather_data, stock_data = fetch_all_data()

        # Log summary of fetched data
        logger.info(f"\n--- fetch_all_data Summary ---")
        logger.info(f"News articles fetched: {len(news_data)}")
        logger.info(f"Weather locations fetched: {len(weather_data)}")
        logger.info(f"Stock tickers fetched: {len(stock_data)}")

        # Log first news item
        if news_data:
            log_response("Sample News Item", news_data[0])

        # Log first weather item
        if weather_data:
            log_response("Sample Weather Item", weather_data[0])

        # Log first stock item
        if stock_data:
            log_response("Sample Stock Item", stock_data[0])

        # Verify we got data
        if news_data and len(news_data) > 0:
            logger.info("\n✅ fetch_all_data Test PASSED")
            return True
        else:
            logger.error("\n❌ fetch_all_data Test FAILED (no news data)")
            return False

    except Exception as e:
        logger.error(f"fetch_all_data Test FAILED: {str(e)}")
        return False


def run_all_tests() -> Dict[str, bool]:
    """
    Run all API tests and return results.

    Returns:
        Dictionary of test names and their pass/fail status
    """
    logger.info("\n" + "=" * 60)
    logger.info("STARTING CHAD LOVES AI API TESTS")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    # Store test results
    results = {}

    # Run each test
    results['NewsAPI'] = test_news_api()
    results['WeatherAPI'] = test_weather_api()
    results['StockAPI'] = test_stock_api()
    results['fetch_all_data'] = test_fetch_all_data()

    # Print final summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    passed = 0
    failed = 0

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if passed_test:
            passed += 1
        else:
            failed += 1

    logger.info(f"\nTotal: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return results


# Entry point for running tests directly
if __name__ == "__main__":
    run_all_tests()
