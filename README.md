# The Story of the Build: Chad Loves AI Dashboard

**Total Build Time: ~52 minutes**

ask for video proof. The app was completed at min 39 imo.

Deployed Dashbaord - https://ez-dash-wl3ecceucp9kdikczkqwer.streamlit.app/

This document chronicles the step-by-step prompts used to build the Chad Loves AI news dashboard application, along with summaries of what was implemented after each prompt.

I enjoyed the fun. Of course I could have used all the claude commands like /plan /dangerously-code /<created_my_own>, or whatever they come out with tommorrow. I simply didn't need to. For me this was about speed, not perfection.

---
## Prompt 0: Build my application based on the my_app.md

## Prompt 1: Stock Price Font Size
> "in the UI the stock prices font is just a little too big. bring down 50%"

### What Was Built:
Added custom CSS to reduce the stock price font size in the Streamlit metrics display. Injected a `<style>` block targeting `[data-testid="stMetricValue"]` with `font-size: 1rem` (50% of the default 2rem).

**File Modified:** `app.py` - Added CSS in `display_stocks_section()`

---

## Prompt 2: Stock Ticker Ordering
> "In the news articles I can see that picked up the stock tickers. Is it picking them in an order because I would them to get picked on ascending stocks mention in the ascending order of the news articles."

### What Was Built:
Changed the stock ticker display order from alphabetical to first-appearance order. Updated the database query from `ORDER BY ticker` to `ORDER BY id` so tickers appear in the order they were first mentioned across news articles.

**File Modified:** `utils/database.py` - Changed SQL query in `get_all_stocks()`

---

## Prompt 3: Date Filter Not Working
> "When I change the date in the stream application on the right side navbar there is not a change in the article list on the page. We may not need a cache json storage."

### What Was Built:
Made the date filter fully functional:
1. Added `get_news_by_date()` method to NewsAPI client for historical queries
2. Updated `fetch_all_data()` to accept a date parameter
3. Added `loaded_date` tracking in session state
4. Rewrote `load_data()` to check cache first, then fetch from API
5. Updated main function to reload data when selected date changes

**Files Modified:**
- `utils/api_clients.py` - Added historical news fetching
- `app.py` - Date-aware data loading and caching

---

## Prompt 4: API Rate Limiting & Location Detection
> "investigate why all of sudden the api for stocks is no longer getting data. Why is the status a 429 when it worked before. Also, make sure to keep a better watch for any country or location mentioned in the news headlines so that location data can be used for the weather API."

### What Was Built:

**Issue 1 - Stock API 429 Fix:**
- Identified root cause: 5-second auto-refresh was making 36-60 API calls/minute, exceeding Tiingo's rate limit
- Changed auto-refresh interval from 5 seconds to 60 seconds
- Updated sidebar label to reflect new interval

**Issue 2 - Location Detection Expansion:**
Completely rewrote `extract_location_from_article()`:
- Added 45+ countries mapped to capital cities (France→Paris, Japan→Tokyo, etc.)
- Added nationality adjective detection (French→Paris, British→London, etc.)
- Added 60+ international cities (London, Tokyo, Sydney, Dubai, etc.)
- Expanded US cities from 40 to 50

**Files Modified:**
- `app.py` - Lines 213, 381 (refresh interval changes)
- `utils/api_clients.py` - Complete rewrite of location extraction logic

---

## Architecture Summary

The final application consists of:

```
ez-dash/
├── app.py                    # Main Streamlit application
├── utils/
│   ├── api_clients.py        # NewsAPI, Weather, Stock API clients
│   ├── database.py           # SQLite in-memory database
│   └── cache.py              # File-based news caching
├── .cache/                   # Cached news data by date
└── requirements.txt          # Python dependencies
```

### Key Features Built:
1. **News Dashboard** - Displays top 5 headlines with expandable details
2. **Weather Integration** - Fetches weather for locations mentioned in news
3. **Stock Tracking** - Extracts company mentions and displays stock prices
4. **Date Filtering** - Browse news from the past 7 days with caching
5. **Auto-Refresh** - Stock prices refresh every 60 seconds
6. **International Support** - Detects 100+ locations worldwide

### APIs Used:
- **NewsAPI** - News headlines and historical articles
- **OpenWeatherMap** - Current weather data
- **Tiingo** - Stock price data

---

*Built with Claude Code in ~52 minutes*
