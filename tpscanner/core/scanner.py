# scanner.py

import datetime

from rich.progress import Progress

from tpscanner.config import config
from tpscanner.logger import logger
from tpscanner.scraper import Scraper
from tpscanner.utils import sleep


class Scanner:
    def __init__(self, level, urls, quantities, wait, headless, console_out, excel_out):
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
        i = 0
        with Progress() as progress:
            task = progress.add_task("Processing items:", total=len(self.urls))

            scraper = Scraper(self.wait, self.headless)
            for url in self.urls:
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

    def remove_unavailable_items(self):
        count = 0
        for _, items in self.individual_deals.items():
            for item in items:
                if item["availability"] is False:
                    items.remove(item)
                    count += 1
        return count

    def find_best_individual_deals(self):
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
                        best_deal_items["seller_reviews"] = item["seller_reviews"]
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
