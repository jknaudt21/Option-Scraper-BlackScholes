# Option-Scraper-BlackScholes

**Author:** Juan Diego Herrera

The code in this repo allows for scraping option data required for the [Black Scholes model](https://en.wikipedia.org/wiki/Black-Scholes_model). Data is scraped from S&P500 companies.

Beyond the standard python libraries, the code requires `pandas`, `bs4` (Beautiful Soup), and `requests` to work properly

## Background

This scraper was originally created for quite a fun [project I worked on](https://samuellee19.github.io/CSCI145_Option_Pricing/?fbclid=IwAR0PG-MuV_9e8WGgxSXR117pcDa2iYmVBk4z5qDZGaiN-NWAfTRdqVPgAMY) regarding the use of neural nets in option pricing. Make sure to check it out! 

Getting access to option data can be quite expensive - especially when getting data in bulk. Datasets are often protected behind a paywall that can range from \$10-100. Furthermore, for those having access to financial tools such as a Bloomberg terminal (I'm looking at you, students), there is often a data quota that should not be exceeded.

That's why I made this scraper.

## Output
This program will scrape the following information about **all** current call contracts for batches of companies in the S&P500. The program will write into a csv called "`SNP.csv`":

- Option price
- Option strike price
- Option time to maturity (in years)
- Underlying stock price
- Underlying stock dividend yield
- Underlying stock implied volatility (this is the best proxy for a stock's volatility)

Multiple runs will be stacked on top of each other

Almost all data is scraped from Yahoo Finance, with the exception of implied volatility, which is scraped from AlphaQuery

## Usage
This scraper is free to use! Just make sure to check out [this project](https://github.com/samuellee19/CSCI145_Option_Pricing) (*my grade **might** or might not depend on page views...*) and star this repo if you find the scraper useful!

On the more technical side, the scraper can be used in either a Jupyter notebook or a plain `.py` file; the code is almost completely identical. That being said, the `.py` file allows for faster [parameter](#Parameters) tuning. The company list for which the scraping occurs comes from [Wikipedia's list](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).

If you're using the `.py` make sure you pass the correct arguments (see below)

**Important:** since the code is extracting a lot of data from several sites in Yahoo Finance and AlphaQuery, sometimes servers will block your IP for accessing their data for small period of time. In the case of a block, the code crashes and ceases execution immediately. I've tried to ameliorate this effect by adding a wait between each batch.

**If the code crashes** due to a server denial (i.e `requests` returned `None`) you can restart the code at the company index the code crashed on and **you can still keep on appending on the same csv file**. 

With all of this in mind, I recommend running this program while the markets are closed since it takes quite some time to run!

## Parameters

Below is a list of the parameters that can be tuned when running  the `.py`. All parameters are optional and have default values. These parameters should be changed manually if using Jupyter.

- `--batches` - the number of company batches to be processed
- `--bs` - the batch size (i.e the number of companys processed per batch)
- `--rf` - risk-free rate used in the output
- `--waitb` - wait time between batches
- `--wait` - wait time between page requests
- `--verbose` - flag that determines whether the program prints progress. Should be 1 or 0
- `--startIdx` - index to start parsing companies from (see [Wikipedia's list](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) to understand the indexing)
