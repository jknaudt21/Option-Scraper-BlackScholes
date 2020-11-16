#!/usr/bin/env python
# coding: utf-8

# # Option Data Scraper for Black Scholes
# This program will scrape the following information about **all** current call contracts for batches of 10 companies in the S&P500. The program will write into a csv called `"SNP.csv"`:
# * Option price
# * Option strike price
# * Option time to maturity (in years)
# * Underlying stock price
# * Underlying stock dividend yield
# * Underlying stock implied volatility
# 
# Almost all data is scraped from Yahoo Finance, with the exception of implied volatility, which is scraped from AlphaQuery

# ## Import dependencies

# In[1]:


from bs4 import BeautifulSoup
import datetime, time
import requests
import pandas as pd
import sched


# ## Helper functions

# In[2]:


def getTickers():
    """Returns the tickers for all the S&P500 companies using the Wikipedia page
    Outputs: 
        tickers - list of tickers for every company in the S&P500
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find("table") # tickers are contained in a table
    tickers = []
    for row in table.find_all('tr'):
            cols = row.find_all('td')
            if cols:
                tickers.append(cols[0].text.strip())
    return tickers


# In[3]:


def getStockVol(ticker):
    """Returns a stock's 30-day implied volatility from alphaqueries
    Inputs:
        ticker     - a string representing a stock's ticker
    Outputs: 
        volatility - implied volatility for the stock 
    """
    url = "https://www.alphaquery.com/stock/"+ ticker+ "/volatility-option-statistics/30-day/iv-mean"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find("table")
    rows = table.find_all('tr') 
    volatility = float(rows[5].find_all('td')[1].text.strip()) # Specific table entry in AlphaQuery containing data
    return volatility


# In[4]:


def getStockData(ticker):
    """Returns a stock's price, dividend yield, and implied volatility
    Inputs:
        ticker      - a string representing a stock's ticker
    Outputs: 
        stock_price - stock's price
        div_yield   - stock's dividend yield
        volatility  - stock's implied volatility
    """
    url = "https://finance.yahoo.com/quote/"+ticker # Change url based on ticker
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table") # tables in Yahoo finance
    
    # Get stock price
    rows = tables[0].find_all('tr') 
    stock_price = rows[3].find_all('td')[1].text.strip() # Item that returns ask price (4th row in a table)
    # Extract ask price by parsing out other data
    x = stock_price.find('x')
    stock_price = float(stock_price[0:x].replace(",","")) # delete any comma to cast to float
    
    # Get dividend yield
    rows = tables[1].find_all('tr') 
    div_yield = rows[5].find_all('td')[1].text.strip()  # Item that returns ask yield (6th row in a table)
    # Extract yield by parsing out other data
    x = div_yield.find('(')
    if "N" not in div_yield[x+1:-2]: # Only set dividend if not 'N/A'
        div_yield = float(div_yield[x+1:-2])/100
    else: 
        div_yield = 0
        
    # Get volatility
    volatility = getStockVol(ticker)
    
    return stock_price, div_yield, volatility


# In[5]:


def getDates(url):
    """Returns all valid option dates for a given Yahoo options url
    Inputs:
        url   - Yahoo finance options url
    Outputs: 
        dates - list of dates (UNIX time) for the underlying ticker
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    dates = []
    selector = soup.find("select")
    for item in list(soup.find("select").children):
        dates.append(int(item['value']))
    return dates


# In[6]:


def getOptionData(url):
    """Returns a list of strike and call prices for a given Yahoo finance option url 
    Inputs:
        url     - string representing Yahoo finance option url
    Outputs: 
        strikes - list of all strike prices
        prices  - list of all call prices
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find("table")
    strikes = []
    prices = []
    for row in table.find_all('tr'): # Iterate through every table entry
        cols = row.find_all('td')
        if cols:
            strikes.append(float(cols[2].text.strip().replace(",",""))) # 3rd column is strike, kill comma to cast
            # Use ask, bid, or last price depending on availability
            ask  = cols[5].text.strip().replace(",","")
            bid  = cols[4].text.strip().replace(",","")
            last = cols[3].text.strip().replace(",","")
            
            ask = float(ask) if ask != "-" else 0
            bid = float(bid) if bid != "-" else 0
            last = float(last) if last != "-" else 0
            
            if ask != 0:
                prices.append(ask)
            elif bid != 0:
                prices.append(bid)
            else:
                prices.append(last)
    return strikes, prices


# ## Scraper
# Here we will iterate through every call contract available the given batch size in the S&P index. At the end we will append the entire dataset to an existing csv

# In[7]:


def scrapeData(startIndex, bs, rf, verbose = True):
    """Writes into a csv the option values for a batch of stock tickers. During execution may print url and company tickers
    Inputs:
        startIndex - company index to start scraping from (0 - 499)
        bs         - integer representing the batch size to scrape
        rf         - risk free rate
        verbose    - boolean that determines if you want output to be printed
    """
    if startIndex < 0 or startIndex >499:
        raise Exception("Invalid start index!")
        
    cols  = ['Stock Price', 'Strike Price', 'Maturity', 'Dividends', 'Volatility', 'Risk-free', 'Call Price']
    results = pd.DataFrame(columns = cols)
    RISK_FREE =  rf

    tickers = getTickers() # list of company tickers
    unixToday = int(time.time()) # Today's date used to calculate maturity 
    frames=[]  # list of dataframes - will be appended to a single df and exported to csv

    # iterate through every ticker
    for i,ticker in enumerate(tickers[startIndex:startIndex+bs]):
        frame = pd.DataFrame(columns = cols) # fresh frame
        
        if verbose:
            print(ticker, (i+startIndex))
        
        # Get stock data
        stock_price, div_yield, volatility = getStockData(ticker)

        # Start option extraction
        url = "https://finance.yahoo.com/quote/"+ticker+"/options"
        if verbose:
            print(url)
        dates = getDates(url)

        # Firt entry receives special treament in case maturity is today
        strikes, prices = getOptionData(url) 
        maturity = (dates[0] - unixToday)/(60*60*24*365.25) # Convert UNIX time difference to fraction of a year
        if maturity <= 0:
            maturity = 1e-5 # trivial maturity for options that expire today

        # Insert data into a dataframe
        frame['Strike Price'] = strikes
        frame['Call Price'] = prices
        frame['Stock Price'] = stock_price
        frame['Dividends'] = div_yield
        frame['Volatility'] = volatility
        frame['Risk-free'] = RISK_FREE
        frame['Maturity'] = maturity

        frames.append(frame) # first entry to dataframes

        # Loop through the rest of the option contracts
        for date in dates[1:]:
            frame = pd.DataFrame(columns = cols)
            url = "https://finance.yahoo.com/quote/"+ticker+"/options"+"?date="+str(date) # Special URL for future dates
           
            if verbose:
                print(url)
            
            maturity = (date - unixToday)/(60*60*24*365.25) # Convert UNIX time difference to fraction of a year
            strikes, call_prices = getOptionData(url)
            # Add data to dataframe
            frame['Strike Price'] = strikes
            frame['Call Price'] =  call_prices
            frame['Stock Price'] = stock_price
            frame['Dividends'] = div_yield
            frame['Volatility'] = volatility
            frame['Risk-free'] = RISK_FREE
            frame['Maturity'] = maturity
            frames.append(frame)
            
        frames.append(results)
        results = pd.concat(frames)
        frames = []
        if verbose:
            print()
            print('----------------------------------------------------')
            print()
    
    # End of main loop, concatenate all frames and export to csv
    results.to_csv('SNP.csv', mode = 'a', index = False, header = False)


# ## Main Loop
# Iterate through the tickers. 
# 
# Change the value of `num_batches` to determine how many batches of tickers (of size `bs`) you'll scrape
# 
# To avoid server denial for too many requests, we sleep for 500 seconds until next batch is scraped
# 
# In the event of a server denial, the program will error out but some data will still have been written on the csv

# In[10]:


cols  = ['Stock Price', 'Strike Price', 'Maturity', 'Dividends', 'Volatility', 'Risk-free', 'Call Price']
start = int(time.time()) # Used for timekeeping 

results = pd.DataFrame(columns = cols)
results.to_csv('SNP.csv', index = False)

num_batches = 3
bs = 10
rf = 0.0088
wait_period = 500


for i in range(num_batches):
    scrapeData(i*bs, bs, rf, True)
    time.sleep(wait_period)

print("Time passed", (int(time.time()) - start), "seconds")

