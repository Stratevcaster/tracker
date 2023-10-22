import sqlite3
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup

# Database setup
def setup_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS investments
                 (date text, ticker text, invested_money real, shares real)''')
    conn.commit()
    return conn, c

def search_yahoo_for_ticker(etf_name):
    search_url = f"https://finance.yahoo.com/lookup?s={etf_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        ticker = soup.find("td", {"data-test": "SYMBOL"}).text
        return ticker
    except AttributeError:
        print("Couldn't find a matching ticker for the given ETF name.")
        return None

# Adding new investment
def add_investment(conn, c, etf_name, invested_money, shares):
    ticker = search_yahoo_for_ticker(etf_name)
    if not ticker:
        print("Investment not added due to lack of ticker information.")
        return

    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO investments (date, ticker, invested_money, shares) VALUES (?, ?, ?, ?)", (date, ticker, invested_money, shares))
    conn.commit()

# Fetching current portfolio
def get_portfolio(c):
    c.execute("SELECT ticker, SUM(invested_money), SUM(shares) FROM investments GROUP BY ticker")
    return c.fetchall()

# Displaying portfolio
def display_portfolio():
    conn, c = setup_db()
    total_invested = 0
    total_current_value = 0

    for ticker, invested_money, shares in get_portfolio(c):
        current_price = yf.Ticker(ticker).history(period='1d').iloc[0]['Close']
        current_value = shares * current_price
        total_invested += invested_money
        total_current_value += current_value

        print(f"Ticker: {ticker}")
        print(f"Invested: ${invested_money:.2f}")
        print(f"Current Value: ${current_value:.2f}")
        print("------------------------")

    print(f"Total Invested: ${total_invested:.2f}")
    print(f"Total Current Value: ${total_current_value:.2f}")

# Example usage:
if __name__ == "__main__":
    # Setup the database
    conn, c = setup_db()

    # Prompting user to input ETF name for new investment
    etf_name = input("Enter the ETF name for a new investment (or press Enter to skip): ")
    if etf_name:
        invested_money = float(input("Enter the amount invested: "))
        shares = float(input("Enter the number of shares: "))
        add_investment(conn, c, etf_name, invested_money, shares)

    # Display current portfolio
    display_portfolio()

    conn.close()
