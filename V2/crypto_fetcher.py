import requests
import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog

def on_search(event=None):
    """Handle the search action when the button is clicked or Enter is pressed."""
    # Get the input from the entry box
    coins_input = entry.get()
    coins = [coin.strip().upper() for coin in coins_input.split(',')]
    
    # Get the user input for PHP investment amount and remove commas if present
    global investment_amount_php
    investment_amount_php_str = simpledialog.askstring("", "Enter the investment amount in PHP:")
    
    if investment_amount_php_str is None:  # If user cancels input, don't proceed
        return

    # Remove commas and convert to float
    investment_amount_php = float(investment_amount_php_str.replace(',', ''))

    # Clear the output text area
    output_text.delete(1.0, tk.END)
    # Fetch the cryptocurrency data
    result = get_crypto_data(coins)
    # Insert the result into the text area
    output_text.insert(tk.END, result)

def get_crypto_data(coins):
    """Fetch cryptocurrency data from CoinMarketCap API."""
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '36f5ddc8-7bfb-4de5-8cdd-907649420a19',  # Your CoinMarketCap API Key
    }
    parameters = {
        'symbol': ','.join(coins)  # Comma-separated list of coin symbols
    }

    response = requests.get(url, headers=headers, params=parameters)

    if response.status_code == 200:
        data = response.json()
        results = []

        for coin in coins:
            if coin in data['data']:
                coin_data = data['data'][coin]
                current_price = coin_data['quote']['USD']['price']
                current_market_cap = coin_data['quote']['USD']['market_cap']
                circulating_supply = coin_data['circulating_supply']
                total_supply = coin_data['total_supply']
                
                # Calculate FDV
                fdv = total_supply * current_price
                
                # Get the price change (24h) directly from the API
                price_change_24h = coin_data['quote']['USD']['percent_change_24h']
                
                # Format the output
                formatted_market_cap = format_market_cap(current_market_cap)
                formatted_circulating_supply = format_supply(circulating_supply)
                formatted_total_supply = format_supply(total_supply)
                formatted_fdv = format_market_cap(fdv)
                
                # Currency conversion (example rate)
                conversion_rate = 56.85  # Example: 1 USD = 56.85 PHP
                projected_prices = []

                # Determine market cap intervals
                intervals = get_market_cap_intervals(current_market_cap)

                for future_market_cap in intervals:
                    projected_price_value = projected_price(future_market_cap, circulating_supply)
                    projected_prices.append((future_market_cap, projected_price_value, projected_price_value * conversion_rate))

                # Creating formatted output
                results.append(f"=================================================\n"
                               f"Name: {coin_data['name']}, Symbol: {coin_data['symbol']}\n"
                               f"Price: ${current_price:.8f}\n"
                               f"Market Cap: {formatted_market_cap}\n"
                               f"Circulating Supply: {formatted_circulating_supply}\n"
                               f"Total Supply: {formatted_total_supply}\n"
                               f"FDV: {formatted_fdv}\n"
                               f"---------------------------------------------------------\n"
                               f"Price Change (24h): {price_change_24h:.2f}%\n"
                               "---------------------------------------------------------\n"
                               f"+-----------------------------+\n"
                               f"|    Projected Prices         |\n"
                               f"+-----------------------------+\n")

                for future_market_cap, projected_price_value, projected_price_peso in projected_prices:
                    results.append(f" - Market Cap: {format_market_cap(future_market_cap)} -> "
                                   f"Projected Price: ${projected_price_value:.8f} ~ {projected_price_peso:.2f} PHP\n")
                
                # Projected ROI section
                results.append("---------------------------------------------------------\n"
                               f"+-----------------------------+\n"
                               f"|    Projected ROI            |\n"
                               f"+-----------------------------+\n")

                investment_amount_usd = investment_amount_php / conversion_rate  # Convert PHP to USD

                for future_market_cap, projected_price_value, projected_price_peso in projected_prices:
                    multiplier = future_market_cap / current_market_cap if current_market_cap > 0 else 0
                    future_value_php = multiplier * investment_amount_php
                    future_value_usd = future_value_php / conversion_rate

                    results.append(f"If {investment_amount_php:,.0f} PHP was invested right now based on the market cap of {format_market_cap(future_market_cap)}, "
                                   f"the ROI would be: {format_currency(future_value_usd)} USD ~ {format_php_currency(future_value_php)}\n")
                
                results.append("=================================================\n")
            else:
                results.append(f"Coin '{coin}' not found.\n")

        return "\n".join(results)
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_market_cap_intervals(current_market_cap):
    """Determine market cap intervals based on current market cap."""
    if current_market_cap <= 50_000_000:
        return [50_000_000, 100_000_000, 150_000_000, 300_000_000, 500_000_000, 700_000_000, 
                1_000_000_000, 1_500_000_000, 2_000_000_000, 5_000_000_000, 7_000_000_000, 10_000_000_000]
    elif current_market_cap <= 100_000_000:
        return [100_000_000, 150_000_000, 300_000_000, 500_000_000, 700_000_000, 
                1_000_000_000, 1_500_000_000, 2_000_000_000, 5_000_000_000, 7_000_000_000, 10_000_000_000]
    elif current_market_cap <= 500_000_000:
        return [500_000_000, 700_000_000, 1_000_000_000, 1_500_000_000, 2_000_000_000, 
                5_000_000_000, 7_000_000_000, 10_000_000_000, 12_000_000_000]
    elif current_market_cap <= 1_000_000_000:
        return [1_000_000_000, 1_500_000_000, 2_000_000_000, 3_000_000_000, 5_000_000_000, 
                7_000_000_000, 10_000_000_000, 12_000_000_000, 15_000_000_000, 18_000_000_000]
    elif current_market_cap <= 3_000_000_000:
        return [3_000_000_000, 5_000_000_000, 7_000_000_000, 10_000_000_000, 12_000_000_000, 
                15_000_000_000, 18_000_000_000, 20_000_000_000, 25_000_000_000]
    else:
        return [5_000_000_000, 7_000_000_000, 10_000_000_000, 12_000_000_000, 15_000_000_000, 
                18_000_000_000, 20_000_000_000, 25_000_000_000, 30_000_000_000, 35_000_000_000, 
                40_000_000_000, 45_000_000_000]

def format_market_cap(market_cap):
    """Format the market cap for readability."""
    if market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.1f} Billion".rstrip(".0")
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.1f} Million".rstrip(".0")
    else:
        return f"${market_cap}"

def format_supply(supply):
    """Format the supply with commas."""    
    return f"{supply:,}" if supply else "N/A"

def projected_price(market_cap, circulating_supply):
    """Calculate the projected price based on future market cap and circulating supply."""
    if circulating_supply > 0:
        return market_cap / circulating_supply
    return 0

def format_currency(amount):
    """Format the currency amount with commas for USD."""
    return f"${amount:,.2f}"

def format_php_currency(amount):
    """Format the PHP currency amount with commas."""
    return f"₱{amount:,.0f}"

# Setting up the main application window
root = tk.Tk()
root.title("Crypto Fetcher by emokid")

# Configuring the input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Creating the label and entry box for cryptocurrency input
label = tk.Label(input_frame, text="Enter Crypto Coin (Symbol):")
label.pack(side=tk.LEFT)  # Position label on the left

entry = tk.Entry(input_frame, width=30)
entry.pack(side=tk.LEFT)  # Position entry box next to label

# Creating the search button
search_button = tk.Button(root, text="Search", command=on_search)
search_button.pack(pady=10)

# Creating a scrolled text area for output
output_text = scrolledtext.ScrolledText(root, width=80, height=30)
output_text.pack(padx=10, pady=10)

# Set focus on entry box
entry.focus()

# Bind the Enter key to the search function
root.bind('<Return>', on_search)

# Start the application
root.mainloop()
