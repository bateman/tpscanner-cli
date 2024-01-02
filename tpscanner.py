# tpscanner.py
from price_scanner import download_html, extract_prices
from save_results import save_intermediate_results, save_best_deals
from best_deal_finder import find_best_deals

import datetime
import argparse


def main():
    # Set up the command line parser
    parser = argparse.ArgumentParser(description="Trovaprezziscanner - URL Scanner")
    
    # Add command line argument for URLs
    parser.add_argument("-u", "--url", nargs='+', help="List of URLs to scan", required=True)
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    # Parse command line arguments
    args = parser.parse_args()

    # Access the list of URLs provided
    urls = args.url
    headless = args.headless
    
    # Save current date and time
    current_datetime = datetime.datetime.now()
    # Format the date and time as a string (you can customize the format)
    formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H-%M-%S")

    print("Scanning the prices for each URL...")
    all_items = {}
    for url in urls:
        html = download_html(url, headless)
        name, items = extract_prices(html)
        all_items[name] = items
        print(f"\nFound {len(items)} items for {name}")
        # sort the list of items by price
        items.sort(key=lambda x: x['price'])
        print(f"Saving the results for for {name} to a spreadsheet...")
        save_intermediate_results(f"results_{formatted_datetime}.xlsx", name, items)
    
    print("\nFinding the best deal...")
    best_deals = find_best_deals(all_items)
    print(f"Found {len(best_deals)} best deals")
    print("Saving best deals to a spreadsheet...\n")
    save_best_deals(f"results_{formatted_datetime}.xlsx", "Best Deals", best_deals)
    print("Done.")

if __name__ == "__main__":
    main()
