# Option-Scraper-BlackScholes
The code in this repo allows for scraping option data required for the [Black Scholes model](https://en.wikipedia.org/wiki/Black-Scholes_model). Data is scraped from S&P500 companies.

## Background

This scraper was originally created for quite a fun [project I worked on](https://github.com/samuellee19/CSCI145_Option_Pricing) regarding the use of neural nets in option pricing. Make sure to check it out!

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

Almost all data is scraped from Yahoo Finance, with the exception of implied volatility, which is scraped from AlphaQuery

## Usage
This scraper is free to use! Just make sure to check out [this project](https://github.com/samuellee19/CSCI145_Option_Pricing) and star this repo if you find the scraper useful!

On the more technical side, the scraper can be used in either a Jupyter notebook or a plain `.py` file; the code is almost completely identical. That being said, the `.py` file allows for faster [parameter](#Parameters) tuning. The company for which the scraping occurs comes from [Wikipedia's list](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).

If you're using the `.py` make sure you pass the correct arguments (see below)

**Important:** since the code is extracting a lot of data from several sites in Yahoo Finance and AlphaQuery, sometimes servers will block your IP for accessing their data for small period of time. In the case of a block, the code crashes and ceases execution immediately. I've tried to ameliorate this effect by adding a wait between each batch.

## Parameters

Below is a list of the parameters that can be tuned when running  the `.py`. These parameters should be changed manually is using Jupyter.

- `--batches` - the number of company batches to be processed. Optional. Default is 5
- `--bs` - the batch size (i.e the number of companys processed per batch). Optional. Default is 10
- `--rf` - risk-free rate used in the output. **Required** Default is 0.0088
- `--wait` - wait time between patches. Optional. Default is 500 seconds
- `--verbose` - flag that determines whether the program prints progress. Should be 1 or 0. Optional. Default is 1
- `--startIdx` - index to start parsing companies from (see [Wikipedia's list](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) to understand the indexing). Optional. Default is 0
