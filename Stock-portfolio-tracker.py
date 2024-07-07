import requests
import pandas as pd
import json
import os
from tabulate import tabulate


class StockPortfolio:
    def __init__(self, file_path='portfolio.json', api_key='A252AZKI9BTSOY98'):
        self.file_path = file_path
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'
        self.portfolio = self.load_portfolio()

    def load_portfolio(self):
        """Load portfolio from file, if it exists."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return []

    def save_portfolio(self):
        """Save portfolio to file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.portfolio, file, indent=4)

    def add_stock(self, symbol, shares, purchase_price):
        """Add a stock to the portfolio."""
        stock_data = {
            'symbol': symbol.upper(),
            'shares': shares,
            'purchase_price': purchase_price,
            'current_price': 0.0,
            'total_value': 0.0,
            'gain_loss': 0.0
        }
        self.portfolio.append(stock_data)
        self.save_portfolio()
        print(f"Added {shares} shares of {symbol.upper()} at ${purchase_price:.2f} each.")

    def remove_stock(self, symbol):
        """Remove a stock from the portfolio."""
        self.portfolio = [stock for stock in self.portfolio if stock['symbol'] != symbol.upper()]
        self.save_portfolio()
        print(f"Removed {symbol.upper()} from the portfolio.")

    def fetch_current_price(self, symbol):
        """Fetch the current price of a stock using Alpha Vantage API."""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': '1min',
                'apikey': self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            time_series = data.get('Time Series (1min)', {})
            if not time_series:
                print(f"No data returned for {symbol}.")
                return None

            latest_time = sorted(time_series.keys())[-1]
            current_price = float(time_series[latest_time]['4. close'])
            return current_price
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def update_current_prices(self):
        """Fetch current prices for all stocks in the portfolio."""
        for stock in self.portfolio:
            current_price = self.fetch_current_price(stock['symbol'])
            if current_price:
                stock['current_price'] = current_price
                stock['total_value'] = stock['shares'] * current_price
                stock['gain_loss'] = (current_price - stock['purchase_price']) * stock['shares']
        self.save_portfolio()

    def calculate_total_value(self):
        """Calculate the total value of the portfolio."""
        return sum(stock['total_value'] for stock in self.portfolio)

    def calculate_total_gain_loss(self):
        """Calculate the total gain or loss of the portfolio."""
        return sum(stock['gain_loss'] for stock in self.portfolio)

    def view_portfolio(self):
        """Display the detailed portfolio information."""
        self.update_current_prices()
        df = pd.DataFrame(self.portfolio)
        print(tabulate(df, headers='keys', tablefmt='grid'))
        print(f"\nTotal Portfolio Value: ${self.calculate_total_value():.2f}")
        print(f"Total Gain/Loss: ${self.calculate_total_gain_loss():.2f}")

    def portfolio_summary(self):
        """Provide a summary of the portfolio."""
        self.update_current_prices()
        stock_summary = []
        for stock in self.portfolio:
            summary = {
                'Symbol': stock['symbol'],
                'Shares': stock['shares'],
                'Purchase Price': stock['purchase_price'],
                'Current Price': stock['current_price'],
                'Total Value': stock['total_value'],
                'Gain/Loss': stock['gain_loss']
            }
            stock_summary.append(summary)
        return stock_summary

    def diversification_analysis(self):
        """Analyze the diversification of the portfolio."""
        self.update_current_prices()
        total_value = self.calculate_total_value()

        if total_value == 0:
            print("Total portfolio value is zero. Diversification analysis cannot be performed.")
            return

        diversification = {stock['symbol']: stock['total_value'] / total_value * 100 for stock in self.portfolio}
        print("\nDiversification Analysis:")
        for symbol, percentage in diversification.items():
            print(f"{symbol}: {percentage:.2f}%")

    def historical_performance(self, symbol):
        """Fetch and display historical performance of a stock using Alpha Vantage API."""
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if 'Time Series (Daily)' in data:
                daily_series = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(daily_series, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={"4. close": "Close"})[["Close"]].sort_index()

                print(f"\nHistorical Performance of {symbol.upper()} for the Last Year:")
                print(tabulate(df.head(365), headers='keys', tablefmt='grid'))  # Show last 365 days
            else:
                print(f"No historical data available for {symbol.upper()}.")
        except Exception as e:
            print(f"Error fetching historical data for {symbol.upper()}: {e}")


def main():
    portfolio = StockPortfolio(api_key='A252AZKI9BTSOY98')

    while True:
        print("\nStock Portfolio Management")
        print("1. Add Stock")
        print("2. Remove Stock")
        print("3. View Portfolio")
        print("4. View Portfolio Summary")
        print("5. Diversification Analysis")
        print("6. Historical Performance")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            symbol = input("Enter stock symbol: ")
            try:
                shares = int(input("Enter number of shares: "))
                purchase_price = float(input("Enter purchase price: "))
                portfolio.add_stock(symbol, shares, purchase_price)
            except ValueError:
                print("Invalid input. Please enter numeric values for shares and purchase price.")
        elif choice == '2':
            symbol = input("Enter stock symbol to remove: ")
            portfolio.remove_stock(symbol)
        elif choice == '3':
            portfolio.view_portfolio()
        elif choice == '4':
            summary = portfolio.portfolio_summary()
            print(tabulate(summary, headers='keys', tablefmt='grid'))
        elif choice == '5':
            portfolio.diversification_analysis()
        elif choice == '6':
            symbol = input("Enter stock symbol for historical performance: ")
            portfolio.historical_performance(symbol)
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
