Here is a prompt that I am about to run through claude-code on my local machine. Make this easy to read for claude sonnet 4.5 and create steps or whatever is needed for the full development cycle of this application. Name it something along the lines of Chad is Crazy AI or Chad Loves AI!


Build an application that integrates data from multiple APIs to display the top news stories of the day, along with relevant weather and stock market information for each news article, using an in-memory SQLite  (or similar) database for managing data.


This task is designed to evaluate your problem-solving skills, resourcefulness, and ability to work with live data and databases while creating a meaningful presentation layer.


### Requirements:


**Data Retrieval:**
Step 1. **Fetch Live Data**:


Use **NewsAPI** to fetch the top 10 news stories. 


API Key: 64bbfa65330e4d838bf9a197505b2e01
Python Documentation url - https://newsapi.org/docs/client-libraries/python


Use OpenWeatherMap to fetch weather data for the location(s) mentioned in the news within the NewsAPI request. 
API Key: b478e44facd0c82ef304e04c80ca9e0f
Curl documentation url - https://openweathermap.org/current


Use **Tiingo** to fetch stock prices for companies mentioned in the news or default to the S&P 500 if no specific company is mentioned from NewsAPI responses. 
API Key: 27465c83310d7739ab0767eb939a179db9241985
Example rest endpoint for latest price - https://api.tiingo.com/tiingo/daily/<ticker>/prices
Request help with token/API KEY 
1. Pass the token directly within the request URL.You can pass the token directly in the request URL by passing the token parameter. For example you would query the https://api.tiingo.com/api/test/ endpoint with the token in URL by adding ?token=.








**Database Layer:**
2. **Use SQLite or any other Database Tech You Feel is Fast For You**:
* Implement database to store and manage the fetched data during runtime.
* Define tables for:
* **News**: id, headline, location, date.
* **Weather**: id, location, temperature, date.
* **Stocks**: id, company, price, date.
3. **Populate Data**:
* Store the API data into the SQLite tables at runtime.
* Establish logical relationships between the data (e.g., link weather to locations in news, stocks to companies mentioned).
4. **Query Data**:
* Retrieve and display:
* The top 10 news headlines.
* Weather data for the first location mentioned in the news.
* Stock prices for mentioned companies or the S&P 500.


Cache data using python cache but only keep a storage of 10 days if news is queried by day


### User Interface: 


5. Create a simple interface to:
* Display the news headlines alongside related weather and stock data.
* Allow the user to filter data by selecting a specific date within the past week.
* Use the Python Package stream lit to build the dashboard and refresh the stock prices every 5 seconds while user is on the page that relate to the stock tickers in the news.


### Simplifications:
6. **SQLite In-Memory Mode**:
* Use SQLite’s in-memory mode (:memory:) to simplify setup.
* All data will exist only during the program’s runtime.
8. **Focus**:
* Avoid unnecessary complexity (e.g., no Docker or containerization).


### RULES TO FOLLOW WHEN DEVELOPING
Please optimize functions like utility functions that can be placed outside of the dashboard for neatness of code.
Please code like a jr software engineer so that others can evaluate the code but use a high level of optimization when coding objects and methods. 
Use docstrings for methods and add comments to every 5 lines of code


### Tools:
* Build a python venv using whatever python I have on my local machine.
* Use a requirements .txt file to keep track of the versions of packages
* Use pythonic methods, but if pythonic styles are used please comment above the logic of the line of code. 
* Use sql lite and optimize for streamlit efficiency 
* build for a vercel deployment
* Make sure to hide my env variables like my API KEYS please!!




Happy Coding :)