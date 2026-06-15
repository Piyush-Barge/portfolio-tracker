# Portfolio Tracker — NSE India

Tired of checking your portfolio across five different tabs? This Python script takes your NSE trade export, grabs live prices, calculates your P&L, and spits out a nice summary in your terminal, a CSV, and a slick HTML report. That's it.

## What it does

- Reads your actual NSE trades — Symbol, date, buy/sell, quantity, price
- Figures out your real cost basis — uses FIFO, so partial sells don't break the math
- Gets live prices — pulls from `yfinance`, automatically adds `.NS` for NSE stocks
- Tells you what you need to know:
  - How much you're holding
  - What you paid for it on average
  - What it's worth right now
  - How much money you're up or down (in rupees and %)
  - What you've already booked (realised gains/losses)
  - What chunk of your portfolio each stock is
- Shows results three ways — console table (pretty), CSV (spreadsheet-friendly), and HTML report (looks good in your browser)

## How it's organized

portfolio-tracker/
├── trades.csv               # Your trade history (input)
├── tracker.py               # The main script
├── portfolio_report.csv     # Auto-generated report (CSV)
├── portfolio_report.html    # Auto-generated report (HTML)
└── README.md

## Getting started

### Step 1: Get the code
```bash
git clone https://github.com/Piyush-Barge/portfolio-tracker.git
cd portfolio-tracker
```

### Step 2: Install what you need
```bash
pip install yfinance pandas tabulate
```

### Step 3: Add your trades
Grab your NSE trade export and save it as `trades.csv`. It should have these columns:

Symbol, ISIN, Trade Date, Exchange, Segment, Series, Trade Type, Auction, Quantity, Price, Trade ID, Order ID, Order Execution Time

Just make sure `Trade Type` is either `buy` or `sell` (lowercase).

### Step 4: Run it
```bash
python tracker.py
```
Done. Check your console, then look for the CSV and HTML files.


## Output

Run the script and you get:
- Console table — shows all holdings with current prices & P&L
- CSV file — `portfolio_report.csv` for spreadsheets
- HTML file — `portfolio_report.html` for browser (nice light theme)

Prices update every time you run it.


## Built with AI

Used Claude (Anthropic) to help build this. Asked it to create a portfolio tracker that reads NSE trades, calculates holdings using FIFO, grabs live prices, and spits out reports. It handled the logic, FIFO calculations, and HTML generation pretty well. Code was tested and works fine.


## Prompt Used:

Build a Python-based portfolio tracker that reads NSE trade history from a CSV file and processes transactions using FIFO accounting. Fetch live stock prices using the yfinance library (NSE tickers with .NS suffix). Compute realised and unrealised P&L for each holding, along with current portfolio value and allocation percentage. Generate output reports in three formats: console table, CSV file, and HTML report for browser viewing.


