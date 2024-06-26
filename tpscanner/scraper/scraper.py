"""This module contains the Scraper class that is responsible for scraping the Trovaprezzi website."""

import random
import re

import undetected_chromedriver as uc
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tpscanner.config import config
from tpscanner.logger import logger
from tpscanner.utils import sleep


class Scraper:
    """Scraper class for scraping the Trovaprezzi website."""

    def __init__(self, wait: int, headless: bool):
        """Initialize the Scraper object with the specified wait time and headless mode.

        Arguments:
            wait (int): The wait time for the WebDriver to wait for an element to be clickable.
            headless (bool): A boolean value indicating whether to run the WebDriver in headless mode.

        """
        self.wait = wait
        self.headless = headless
        self.driver = self._setup_driver()

    def _setup_driver(self):
        chrome_options = None
        if self.headless:
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument(
                f"user-agent={random.choice(config.user_agents)}"  # noqa S311
            )
            # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--ignore-certificate-errors")

        driver = None
        if self.headless:
            logger.info("Using undetected_chromedriver for headless mode.")
            driver = uc.Chrome(
                headless=self.headless,
                use_subprocess=False,
                options=chrome_options,
                version_main=config.chrome_version,
            )
        else:
            logger.info("Using regular chromedriver for non-headless mode.")
            driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)
        return driver

    def _navigate_to_url(self, url):
        self.driver.get(url)
        # wait seconds before next URL to avoid being blocked and captcha
        sleep(config.sleep_rate_limit)
        try:
            WebDriverWait(self.driver, self.wait).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary")
                )
            ).click()
        except Exception:
            logger.warn(
                "The cookie message did not appear, trying to move on without accepting."
            )

    def download_html(self, url: str) -> tuple:
        """Download the HTML content of the specified URL.

        Arguments:
            url (str): The URL to download the HTML content from.

        Returns:
            tuple: A tuple containing the HTML content of the page.

        """
        self._navigate_to_url(url)
        # Click on show more offers button
        # while True:
        #     try:
        #         WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='more_offers button link-arrow data-link']"))).click()
        #     except Exception:
        #         # no more offers (the button is not present anymore)
        #         break
        html_content_plus_shipping = self.driver.page_source
        # wait seconds before next URL to avoid being blocked and captcha
        sleep(config.sleep_rate_limit)
        try:
            WebDriverWait(self.driver, self.wait).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".include_shipping"))
            ).click()
        except Exception:
            logger.critical("An error occurred while scraping the page.")
            self.driver.save_screenshot("error.png")
            raise
        html_content_including_hipping = self.driver.page_source
        return html_content_plus_shipping, html_content_including_hipping

    def extract_prices_plus_shipping(self, html_content: str, quantity: int) -> tuple:
        """Extract the prices of the items plus shipping cost from the HTML content.

        Arguments:
            html_content (str): The HTML content to extract the prices from.
            quantity (int): The quantity of items to buy.

        Returns:
            tuple: A tuple containing the item name and a list of items.

        """
        results = []
        item_name = ""
        try:
            tree = html.fromstring(html_content)

            # Use XPath to access the sellers and items
            temp = tree.xpath(
                '//div[@class="name_and_rating"]/h1/strong/text() | //div[@class="name_and_rating"]/h1/text()[normalize-space()] | //div[@class="search_results_heading"]/h1/strong/text()'
            )
            temp = [item.strip() for item in temp]
            item_name = " ".join(temp)
            if not item_name:
                logger.error("No item name found, going with default.")
                raise Exception("No item name found.")

            elements = tree.xpath('//*[@id="listing"]/ul/li')
            for element in elements:
                merchant = element.xpath(
                    'div[@class="item_info"]/div[@class="item_merchant"]/div/a/span'
                )[0].text.strip()
                merchant_link = element.xpath(
                    'div[@class="item_info"]/div[@class="item_merchant"]/div/a/@href'
                )[0]
                merchant_reviews = element.xpath(
                    'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[@class="merchant_reviews"]'
                )[0].text.strip()
                merchant_reviews_link = element.xpath(
                    'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a/@href'
                )[0]
                try:
                    merchant_rating = element.xpath(
                        'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[starts-with(@class, "merchant_reviews rating_image")]'
                    )[0].get("class")
                except Exception:
                    merchant_rating = None
                price = element.xpath(
                    'div[@class="item_price "]/div[@class="item_basic_price"]'
                )[0].text.strip()
                try:
                    delivery_price = element.xpath(
                        'div[@class="item_price "]/div[@class="item_delivery_price "]'
                    )[0].text.strip()
                except Exception:
                    delivery_price = None
                try:
                    free_delivery = element.xpath(
                        'div[@class="item_price "]/div[@class="free_shipping_threshold"]/span/span/span'
                    )[0].text.strip()
                except Exception:
                    free_delivery = None
                try:
                    availability = element.xpath(
                        'div[@class="item_price "]/div[@class="item_availability"]/span/@class'
                    )[0]
                except Exception:
                    availability = "not available"
                offer_link = element.xpath('div[@class="item_actions"]/a/@href')[0]
                # convert item values to the appropriate data types
                item = self._convert_data_types(
                    merchant,
                    merchant_link,
                    merchant_reviews,
                    merchant_reviews_link,
                    merchant_rating,
                    price,
                    quantity,
                    delivery_price,
                    free_delivery,
                    availability,
                    offer_link,
                )
                results.append(item)
        except Exception as e:
            message = (
                "Error during scraping. "
                + "Consider removing --headless option and try again."
                if self.headless
                else ""
            )
            logger.critical(message)
            self.driver.save_screenshot("error.png")
            raise e

        return item_name, results

    def extract_best_price_shipping_included(
        self, html_content: str, quantity: int
    ) -> tuple:
        """Extract the best price of the item shipping included from the HTML content.

        Arguments:
            html_content (str): The HTML content to extract the prices from.
            quantity (int): The quantity of items to buy.

        Returns:
            tuple: A tuple containing the item name and the best price item.

        """
        item = {}
        item_name = ""
        try:
            # Parse the HTML content using lxml
            tree = html.fromstring(html_content)

            # Use XPath to access the sellers and items
            temp = tree.xpath(
                '//div[@class="name_and_rating"]/h1/strong/text() | //div[@class="name_and_rating"]/h1/text()[normalize-space()]'
            )
            temp = [item.strip() for item in temp]
            item_name = " ".join(temp)

            # we only need the first item (best price shipping included)
            element = tree.xpath('//*[@id="listing"]/ul/li')[0]

            merchant = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div/a/span'
            )[0].text.strip()
            merchant_link = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div/a/@href'
            )[0]
            merchant_reviews = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[@class="merchant_reviews"]'
            )[0].text.strip()
            merchant_reviews_link = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a/@href'
            )[0]
            try:
                merchant_rating = element.xpath(
                    'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[starts-with(@class, "merchant_reviews rating_image")]'
                )[0].get("class")
            except Exception:
                merchant_rating = None
            price = element.xpath(
                'div[@class="item_price total_price_sorting"]/div[@class="item_basic_price"]'
            )[0].text.strip()
            delivery_price = None
            try:
                free_delivery = element.xpath(
                    'div[@class="item_price total_price_sorting"]/div[@class="free_shipping_threshold"]/span/span/span'
                )[0].text.strip()
            except Exception:
                free_delivery = None
            try:
                availability = element.xpath(
                    'div[@class="item_price total_price_sorting"]/div[@class="item_availability"]/span/@class'
                )[0]
            except Exception:
                availability = "not available"
            offer_link = element.xpath('div[@class="item_actions"]/a/@href')[0]
            # convert item values to the appropriate data types
            item = self._convert_data_types(
                merchant,
                merchant_link,
                merchant_reviews,
                merchant_reviews_link,
                merchant_rating,
                price,
                quantity,
                delivery_price,
                free_delivery,
                availability,
                offer_link,
            )
        except Exception as e:
            message = (
                "Error during scraping. "
                + "Consider removing --headless option and try again."
                if self.headless
                else ""
            )
            logger.critical(message)
            self.driver.save_screenshot("error.png")
            raise e

        return item_name, item

    def _convert_data_types(
        self,
        merchant,
        merchant_link,
        merchant_reviews,
        merchant_reviews_link,
        merchant_rating,
        price,
        quantity,
        delivery_price,
        free_delivery,
        availability,
        offer_link,
    ):
        number_pattern = re.compile(r"\b\d+[,.]?\d*\b")
        item = {}

        item["seller"] = merchant
        item["seller_link"] = "https://www.trovaprezzi.it" + merchant_link
        merchant_reviews = number_pattern.search(merchant_reviews).group()
        item["seller_reviews"] = int(merchant_reviews.replace(".", ""))
        item["seller_reviews_link"] = (
            "https://www.trovaprezzi.it" + merchant_reviews_link
        )
        price = number_pattern.search(price).group()
        if merchant_rating:
            merchant_rating = merchant_rating.split(" ")[2].replace("rate", "")
            merchant_rating = int(merchant_rating) / 10.0
        item["seller_rating"] = merchant_rating
        item["price"] = float(price.replace(",", "."))
        item["quantity"] = quantity
        if delivery_price:
            delivery_price = number_pattern.search(delivery_price).group()
            item["delivery_price"] = float(delivery_price.replace(",", "."))
        else:
            item["delivery_price"] = 0.0
        item["total_price"] = item["price"] * quantity
        if free_delivery:
            free_delivery = number_pattern.search(free_delivery).group()
            item["free_delivery"] = float(free_delivery.replace(",", "."))
        else:
            item["free_delivery"] = free_delivery
        if free_delivery and item["total_price"] >= item["free_delivery"]:
            item["total_price_plus_delivery"] = item["total_price"]
        else:
            item["total_price_plus_delivery"] = (
                item["total_price"] + item["delivery_price"]
            )
        item["availability"] = True if availability == "available" else False
        item["link"] = "https://www.trovaprezzi.it" + offer_link

        return item
