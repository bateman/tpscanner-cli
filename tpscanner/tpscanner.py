# tpscanner.py

import argparse
from datetime import datetime

from tpscanner import io
from tpscanner.core import Scanner
from tpscanner.logger import logger
from tpscanner.ui import Console


def main():
    # Set up the command line parser
    parser = setup_cli_parser()

    # Parse command line arguments
    (
        level,
        urls,
        quantities,
        filter_not_available,
        wait,
        headless,
        console_out,
        excel_out,
    ) = parse_command_line(parser)

    # Set the logging level
    logger.set_log_level(level)
    logger.info(f"Logging level: {level}")

    # Save current date and time in the desired format
    formatted_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    console = Console()
    # Start the scanner
    console.print(message="TrovaPrezzi Scanner", level="start")
    scanner = Scanner(level, urls, quantities, wait, headless, console_out, excel_out)
    logger.info("Scanning the deals for each item.")
    scanner.scan()
    logger.info("Saving individual deals.")
    io.save_individual_deals(
        f"results_{formatted_datetime}.xlsx", scanner.individual_deals
    )
    if filter_not_available:
        logger.info("Removing items marked as not available.")
        count = scanner.remove_unavailable_items()
        logger.info(f"{count} items removed.")
    logger.info("Finding best individual deals.")
    scanner.find_best_individual_deals()
    logger.info(f"Found {len(scanner.best_individual_deals)} individual best deals.")

    if scanner.best_individual_deals:
        if excel_out:
            logger.info("Saving best individual deals.")
            io.save_best_individual_deals(
                f"results_{formatted_datetime}.xlsx",
                "Best Individual Deals",
                scanner.best_individual_deals,
            )
        if console_out:
            logger.info("Displaying best individual deals in console.")
            console.display_best_individual_deals(
                scanner.best_individual_deals,
                f"Best Individual Deals ({len(scanner.best_individual_deals)})",
            )

    if len(urls) > 1:
        logger.info("Finding the best cumulative deals.")
        scanner.find_best_cumulative_deals()
        logger.info(f"Found {len(scanner.best_cumulative_deals)} best deals.")
        if excel_out:
            logger.info("Saving best cumulative deals.")
            io.save_best_cumulative_deals(
                f"results_{formatted_datetime}.xlsx",
                "Best Cumulative Deals",
                scanner.best_cumulative_deals,
            )
        if console_out:
            logger.info("Displaying best cumulative deals in console.")
            console.display_best_cumulative_deals(
                scanner.best_cumulative_deals,
                f"Best Cumulative Deals ({len(scanner.best_cumulative_deals)})",
            )

    console.print(message="Done", level="end")


def setup_cli_parser():
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
        "-n",
        "--notavailable",
        default=True,
        help="Remove items marked as not available",
    )
    parser.add_argument(
        "-w", "--wait", type=int, help="Wait time between URLs requests", required=False
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument(
        "-c",
        "--console",
        default=True,
        help="Show output in console",
    )
    parser.add_argument("-x", "--excel", default=True, help="Save output to Excel file")
    return parser


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

    # Retrieve the list of quantities for each URL provided
    quantities = args.quantity
    if not quantities:
        quantities = [1] * len(urls)

    # Whether to remove items marked as not available
    filter_not_available = args.notavailable or True

    # Retrieve the wait time between URLs requests
    wait = args.wait
    if not wait:
        wait = 5
    # Whether to run in headless mode
    headless = args.headless
    # Whether to show output in console
    console_out = args.console
    # Whether to save output to Excel file
    excel_out = args.excel
    return (
        level.lower(),
        urls,
        quantities,
        filter_not_available,
        wait,
        headless,
        console_out,
        excel_out,
    )


if __name__ == "__main__":
    main()
