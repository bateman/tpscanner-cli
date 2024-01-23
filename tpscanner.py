# tpscanner.py

from price_scanner import (
    download_html,
    extract_prices_plus_shipping,
    extract_best_price_shipping_included,
)
from save_results import save_intermediate_results, save_best_cumulative_deals
from best_deal_finder import find_best_deals, remove_unavailable_items

import datetime
import argparse
import time


def main():
    # Set up the command line parser
    parser = argparse.ArgumentParser(description="Trovaprezziscanner - URL Scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", nargs="+", help="List of URLs to scan")
    group.add_argument("-f", "--file", help="File containing URLs to scan")
    parser.add_argument(
        "-q",
        "--quantity",
        nargs="+",
        help="List of quantities to buy for each URL (in order)",
        required=False,
    )
    parser.add_argument(
        "-w", "--wait", type=int, help="Wait time between URLs requests", required=False
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    # Parse command line arguments
    urls, quantities, wait, headless = parse_command_line(parser)

    # Save current date and time in the desired format
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H-%M-%S")

    print("Scanning the prices for each URL...")
    all_items = {}
    i = 0
    for url in urls:
        quantity = int(quantities[i])
        i += 1
        # download prices plus shipping costs (html1) and best price with shipping costs included (html2)
        html1, html2 = download_html(url, wait, headless)
        name, items = extract_prices_plus_shipping(html1, quantity)
        _, item = extract_best_price_shipping_included(html2, quantity)
        if item not in items:
            items.append(item)
        all_items[name] = items
        print(f"\nFound {len(items)} items for {name}")
        # sort the list of items by price
        items.sort(key=lambda x: x["price"])
        print(f"Saving the results for for {name} to a spreadsheet...")
        save_intermediate_results(f"results_{formatted_datetime}.xlsx", name, items)
        # wait seconds before next URL
        time.sleep(wait)

    print("\nRemoving items marked as not available...")
    all_items, count = remove_unavailable_items(all_items)
    print(f"{count} items removed")
    print("\nFinding the best cumulative deals...")
    best_cumulative_deals = find_best_deals(all_items)
    print(f"Found {len(best_cumulative_deals)} best deals")
    print("Saving best deals to the spreadsheet...\n")
    save_best_cumulative_deals(
        f"results_{formatted_datetime}.xlsx",
        "Best Cumulative Deals",
        best_cumulative_deals,
    )
    print("Done.")


def parse_command_line(parser):
    args = parser.parse_args()

    # Retrieve the list of URLs provided
    urls = args.url
    quantities = []
    if not urls:
        urls = []
        # Read the URLs from the file provided
        with open(args.file, "r") as f:
            lines = f.read().splitlines()
        for line in lines:
            # remove any trailing or leading whitespaces
            line = line.strip()
            # if line contains whitespaces in between, split and retrieve the quantity
            if " " in line:
                url, q = line.split()
                urls.append(url)
                quantities.append(q)
            else:
                urls.append(line)

    if not quantities:
        # Retrieve the list of quantities for each URL provided
        quantities = args.quantity
        if not quantities:
            quantities = [1] * len(urls)
    # Retrieve the wait time between URLs requests
    wait = args.wait
    if not wait:
        wait = 5
    # Whether to run in headless mode
    headless = args.headless
    return urls, quantities, wait, headless


if __name__ == "__main__":
    main()
