# tpscanner.py

import argparse
import datetime
import time
from rich.progress import Progress
from tpscanner.logger import logger
from tpscanner.config import config


from tpscanner.deals_finder import (
    find_best_deals,
    find_individual_best_deals,
    remove_unavailable_items,
)
from tpscanner.price_scanner import (
    download_html,
    extract_best_price_shipping_included,
    extract_prices_plus_shipping,
)
from tpscanner.save_results import (
    save_best_cumulative_deals,
    save_best_individual_deals,
    save_intermediate_results,
)


def main():
    # Set up the command line parser
    parser = argparse.ArgumentParser(description="TrovaPrezzi Scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", nargs="+", help="List of URLs to scan")
    group.add_argument("-f", "--file", help="File containing URLs to scan")
    parser.add_argument(
        "-l", "--level", help="Logging level (debug, info, warning, error, critical)"
    )
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
    level, urls, quantities, wait, headless = parse_command_line(parser)

    # Set the logging level
    logger.set_log_level(level)
    logger.debug(f"Logging level: {level}")

    # Save current date and time in the desired format
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H-%M-%S")

    logger.start("TrovaPrezzi Scanner")
    logger.info("Scanning the item prices for each URL.")
    all_items = {}
    i = 0
    with Progress() as progress:
        task = progress.add_task("Processing URLs.", total=len(urls))

        for url in urls:
            if progress.finished:
                break
            quantity = int(quantities[i])
            i += 1
            # download prices plus shipping costs (html1) and best price with shipping costs included (html2)
            html1, html2 = download_html(url, wait, headless)
            name, items = extract_prices_plus_shipping(html1, quantity)
            _, item = extract_best_price_shipping_included(html2, quantity)
            if item not in items:
                items.append(item)
            all_items[name] = items
            logger.info(f"Found {len(items)} items for `{name}`.")
            # sort the list of items by price
            items.sort(key=lambda x: x["price"])
            logger.debug(f"Saving the results for for `{name}` to spreadsheet.")
            save_intermediate_results(f"results_{formatted_datetime}.xlsx", name, items)
            # wait seconds before next URL to avoid being blocked and captcha
            time.sleep(config.sleep_rate_limit)
            progress.update(task, advance=1)

    logger.debug("Removing items marked as not available.")
    all_items, count = remove_unavailable_items(all_items)
    logger.debug(f"{count} items removed.")
    logger.info("Checking the presence of individual best deals.")
    best_individual_deals = find_individual_best_deals(all_items)
    logger.info(f"Found {len(best_individual_deals)} individual best deals.")
    if best_individual_deals:
        logger.debug("Saving best individual deals.")
        save_best_individual_deals(
            f"results_{formatted_datetime}.xlsx",
            "Best Individual Deals",
            best_individual_deals,
        )
    logger.info("Finding the best cumulative deals.")
    best_cumulative_deals = find_best_deals(all_items)
    logger.info(f"Found {len(best_cumulative_deals)} best deals.")
    logger.debug("Saving best cumulative deals.")
    save_best_cumulative_deals(
        f"results_{formatted_datetime}.xlsx",
        "Best Cumulative Deals",
        best_cumulative_deals,
    )
    logger.end("Done.")


def parse_command_line(parser):
    args = parser.parse_args()

    # Retrieve the logging level
    level = args.level or "info"

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
    return level, urls, quantities, wait, headless


if __name__ == "__main__":
    main()
