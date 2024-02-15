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
        includena,
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
    if not includena:
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
                "Best individual deals",
                scanner.best_individual_deals,
            )
        if console_out:
            logger.info("Displaying best individual deals in console.")
            console.display_best_individual_deals(
                scanner.best_individual_deals,
                f"Individual deals unlocking free delivery ({len(scanner.best_individual_deals)})",
            )

    if len(urls) > 1:
        logger.info("Finding the best cumulative deals.")
        scanner.find_best_cumulative_deals()
        logger.info(f"Found {len(scanner.best_cumulative_deals)} best deals.")
        if excel_out:
            logger.info("Saving best cumulative deals.")
            io.save_best_cumulative_deals(
                f"results_{formatted_datetime}.xlsx",
                "Best cumulative deals",
                scanner.best_cumulative_deals,
            )
        if console_out:
            logger.info("Displaying best cumulative deals in console.")
            console.display_best_cumulative_deals(
                scanner.best_cumulative_deals,
                f"Best cumulative deals ({len(scanner.best_cumulative_deals)})",
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
        "-i",
        "--includena",
        action="store_true",
        help="Include items marked as not available",
    )
    parser.add_argument(
        "-w", "--wait", type=int, help="Wait time between URLs requests", required=False
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument(
        "-c",
        "--console",
        action="store_true",
        help="Show output in console",
    )
    parser.add_argument(
        "-x", "--excel", action="store_true", help="Save output to Excel file"
    )
    return parser


def parse_command_line(parser):
    args = parser.parse_args()

    # Retrieve the logging level
    level = args.level or ""

    # Retrieve the list of URLs provided from the command line
    urls = args.url
    if urls:
        # Retrieve also the list of quantities for each URL provided from the command line
        quantities = args.quantity
    else:
        # Read the URLs and quantities from the file provided
        quantities = []
        urls = []
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
    # final check in case no quantities were provided in the file or command line
    if not quantities:
        quantities = [1] * len(urls)

    # Whether to include items marked as not available
    includena = args.includena

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
        includena,
        wait,
        headless,
        console_out,
        excel_out,
    )


if __name__ == "__main__":
    main()
