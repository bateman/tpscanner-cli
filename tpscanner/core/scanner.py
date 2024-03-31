"""This module contains the Scanner class that is responsible for scanning the URLs and extracting the prices and shipping costs."""

import datetime

from rich.progress import Progress

from tpscanner.config import config
from tpscanner.logger import logger
from tpscanner.scraper import Scraper
from tpscanner.utils import sleep


class Scanner:
    """Scanner class that is responsible for scanning the URLs and extracting the prices and shipping costs.

    Attributes:
        level (str): The level of the scanner.
        urls (list): The list of URLs to scan.
        quantities (list): The list of quantities for each URL.
        wait (int): The number of seconds to wait before scraping the next URL.
        headless (bool): The headless mode of the browser.
        console_out (bool): The console output flag.
        excel_out (bool): The Excel output flag.
        individual_deals (dict): The dictionary of individual deals.
        best_individual_deals (list): The list of best individual deals.
        best_cumulative_deals (dict): The dictionary of best cumulative deals.
        formatted_datetime (str): The formatted datetime string.

    Methods:
        scan(): Scans the URLs and extracts the prices and shipping costs.
        remove_unavailable_items(): Removes the unavailable items from the individual deals.
        find_best_individual_deals(): Finds the best individual deals.
        find_best_cumulative_deals(): Finds the best cumulative deals.

    """

    def __init__(self, level, urls, quantities, wait, headless, console_out, excel_out):
        """Initialize the Scanner object with the specified parameters.

        Arguments:
            level (str): The level of the scanner.
            urls (list): The list of URLs to scan.
            quantities (list): The list of quantities for each URL.
            wait (int): The number of seconds to wait before scraping the next URL.
            headless (bool): The headless mode of the browser.
            console_out (bool): The console output flag.
            excel_out (bool): The Excel output flag.

        """
        self.level = level
        self.urls = urls
        self.quantities = quantities
        self.wait = wait
        self.headless = headless
        self.console_out = console_out
        self.excel_out = excel_out
        self.individual_deals = {}
        self.best_individual_deals = []
        self.best_cumulative_deals = {}
        self.formatted_datetime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    def scan(self):
        """Scan the URLs and extracts the prices and shipping costs.

        This method iterates over the list of URLs and performs the following steps for each URL:
        1. Creates an instance of the Scraper class with the specified wait time and headless mode.
        2. Downloads the HTML content for the URL, including prices plus shipping costs and best prices with shipping costs included.
        3. Extracts the item name and a list of items with their respective prices and shipping costs.
        4. Extracts the best price with shipping costs included.
        5. If the best price is not already in the list of items, it is added.
        6. Sorts the list of items by price.
        7. Stores the list of items in the individual_deals dictionary with the item name as the key.
        8. Logs the number of deals found for the item.
        9. Waits for a specified amount of time before processing the next URL.

        Note: This method uses the Progress class from the rich.progress module to display a progress bar during the scanning process.

        """
        i = 0
        with Progress() as progress:
            task = progress.add_task("Processing items:", total=len(self.urls))

            for url in self.urls:
                scraper = Scraper(self.wait, self.headless)
                if progress.finished:
                    break
                quantity = int(self.quantities[i])
                i += 1
                # download prices plus shipping costs and best prices with shipping costs included (html2)
                (
                    html_deals_plus_shipping,
                    html_deals_shipping_inclued,
                ) = scraper.download_html(url)
                name, items = scraper.extract_prices_plus_shipping(
                    html_deals_plus_shipping, quantity
                )
                _, item = scraper.extract_best_price_shipping_included(
                    html_deals_shipping_inclued, quantity
                )
                if item not in items:
                    items.append(item)
                # sort the list of items by price
                items.sort(key=lambda x: x["price"])
                self.individual_deals[name] = items
                logger.info(f"Found {len(items)} deals for `{name}`.")
                # wait seconds before next URL to avoid being blocked and captcha
                sleep(config.sleep_rate_limit)
                progress.update(task, advance=1)

    def remove_unavailable_items(self) -> int:
        """Remove the unavailable items from the individual deals.

        Returns:
            int: The count of removed items.

        """
        count = 0
        for _, items in self.individual_deals.items():
            for item in items:
                if item["availability"] is False and "Amazon" not in item["seller"]:
                    items.remove(item)
                    count += 1
        return count

    def find_best_individual_deals(self):
        """Find the best individual deals.

        This method iterates over the items in the `individual_deals` dictionary and checks if the seller indicates a free delivery
        threshold and if the cumulative price is greater than or equal to the threshold. If both conditions are met, the item is
        considered as one of the best individual deals and is added to the `best_individual_deals` list.

        """
        for item_name, items_list in self.individual_deals.items():
            for item in items_list:
                # if the seller indicates a free delivery threshold and the cumulative price is greater than or equal to the threshold
                if (
                    item["free_delivery"]
                    and item["total_price"] >= item["free_delivery"]
                ):
                    item["name"] = item_name
                    self.best_individual_deals.append(item)

    def find_best_cumulative_deals(self):
        """Find the best cumulative deals.

        This method iterates over the items in the `individual_deals` dictionary and checks if the seller indicates a free delivery
        threshold and if the cumulative price is greater than or equal to the threshold. If both conditions are met, the item is
        considered as one of the best individual deals and is added to the `best_individual_deals` list.


        """
        # find the common sellers
        common_sellers = []
        for _, items in self.individual_deals.items():
            common_sellers.append([item["seller"] for item in items])
        common_sellers = set(common_sellers[0]).intersection(*common_sellers)

        # for each common seller find, find the cumulative price of all items sold by that seller
        # and sort the items by price
        for seller in common_sellers:
            best_deal_items = {}
            for item_name, items_list in self.individual_deals.items():
                for item in items_list:
                    if item["seller"] == seller:
                        best_deal_items["name"] = item_name
                        best_deal_items["seller"] = item["seller"]
                        best_deal_items["seller_link"] = item["seller_link"]
                        best_deal_items["seller_reviews"] = item["seller_reviews"]
                        best_deal_items["seller_reviews_link"] = item[
                            "seller_reviews_link"
                        ]
                        best_deal_items["seller_rating"] = item["seller_rating"]
                        best_deal_items["delivery_price"] = item["delivery_price"]
                        best_deal_items["free_delivery"] = item["free_delivery"]
                        best_deal_items["availability"] = item["availability"]
                        best_deal_items["link"] = item["link"]
                        best_deal_items["cumulative_price"] = (
                            best_deal_items.get("cumulative_price", 0)
                            + item["total_price"]  # total_price is quantity * price
                        )
            self.best_cumulative_deals[seller] = best_deal_items

        # add the delivery price to the cumulative price if the cumulative price is less than the free delivery price threshold
        for seller, item in self.best_cumulative_deals.items():
            # if the seller indicates a free delivery threshold and the cumulative price is greater than or equal to the threshold
            if (
                item["free_delivery"]
                and item["cumulative_price"] >= item["free_delivery"]
            ):
                item["cumulative_price_plus_delivery"] = item["cumulative_price"]
            else:
                item["cumulative_price_plus_delivery"] = (
                    item["cumulative_price"] + item["delivery_price"]
                )
            self.best_cumulative_deals[seller] = item

        # sort best deals by price
        self.best_cumulative_deals = sorted(
            self.best_cumulative_deals.values(),
            key=lambda x: x["cumulative_price_plus_delivery"],
        )
