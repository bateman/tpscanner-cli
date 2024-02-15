# pricescanner.py

import re

from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tpscanner.config import config


def download_html(url, wait=5, headless=True):
    html_content = None
    try:
        # Set up Chrome options for headless browsing
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument(f"user-agent={config.user_agent}")

        # Use webdriver_manager to automatically download and manage ChromeDriver
        with webdriver.Chrome(
            service=ChromeService(), options=chrome_options
        ) as driver:
            driver.maximize_window()
            # Navigate to the URL
            driver.get(url)

            # Accept cookies
            WebDriverWait(driver, wait).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary")
                )
            ).click()

            # Click on show more offers button
            # while True:
            #     try:
            #         WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='more_offers button link-arrow data-link']"))).click()
            #     except Exception:
            #         # no more offers (the button is not present anymore)
            #         break

            # Get the new HTML content
            html_content = driver.page_source

            # Click on the swicth to show items with shipping costs included
            WebDriverWait(driver, wait).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".include_shipping"))
            ).click()
            html_content_shipping = driver.page_source
    except Exception as e:
        raise (f"Error downloading HTML content: {e}")

    return html_content, html_content_shipping


def extract_prices_plus_shipping(html_content, quantity):
    results = []
    item_name = ""
    try:
        # Parse the HTML content using lxml
        tree = html.fromstring(html_content)

        # Use XPath to access the sellers and items
        item_name = tree.xpath(
            '//div[@class="name_and_rating"]/h1/strong/text() | //div[@class="name_and_rating"]/h1/text()[normalize-space()]'
        )
        item_name = [item.strip() for item in item_name]
        item_name = " ".join(item_name)

        elements = tree.xpath('//*[@id="listing"]/ul/li')
        for element in elements:
            merchant = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div/a/span'
            )[0].text.strip()
            merchant_reviews = element.xpath(
                'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[@class="merchant_reviews"]'
            )[0].text.strip()
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
            availability = element.xpath(
                'div[@class="item_price "]/div[@class="item_availability"]/span/@class'
            )[0]
            offer_link = element.xpath('div[@class="item_actions"]/a/@href')[0]
            # convert item values to the appropriate data types
            item = _convert_data_types(
                merchant,
                merchant_reviews,
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
        raise (f"Error extracting prices: {e}")

    return item_name, results


def extract_best_price_shipping_included(html_content, quantity):
    item = {}
    item_name = ""
    try:
        # Parse the HTML content using lxml
        tree = html.fromstring(html_content)

        # Use XPath to access the sellers and items
        item_name = tree.xpath(
            '//div[@class="name_and_rating"]/h1/strong/text() | //div[@class="name_and_rating"]/h1/text()[normalize-space()]'
        )
        item_name = [item.strip() for item in item_name]
        item_name = " ".join(item_name)

        # we only need the first item (best price shipping included)
        element = tree.xpath('//*[@id="listing"]/ul/li')[0]

        merchant = element.xpath(
            'div[@class="item_info"]/div[@class="item_merchant"]/div/a/span'
        )[0].text.strip()
        merchant_reviews = element.xpath(
            'div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/a[@class="merchant_reviews"]'
        )[0].text.strip()
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
        availability = element.xpath(
            'div[@class="item_price total_price_sorting"]/div[@class="item_availability"]/span/@class'
        )[0]
        offer_link = element.xpath('div[@class="item_actions"]/a/@href')[0]
        # convert item values to the appropriate data types
        item = _convert_data_types(
            merchant,
            merchant_reviews,
            merchant_rating,
            price,
            quantity,
            delivery_price,
            free_delivery,
            availability,
            offer_link,
        )
    except Exception as e:
        raise (f"Error extracting prices: {e}")

    return item_name, item


def _convert_data_types(
    merchant,
    merchant_reviews,
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
    merchant_reviews = number_pattern.search(merchant_reviews).group()
    item["seller_reviews"] = int(merchant_reviews.replace(".", ""))
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
        item["total_price_plus_delivery"] = item["total_price"] + item["delivery_price"]
    item["availability"] = True if availability == "available" else False
    item["link"] = "https://www.trovaprezzi.it" + offer_link

    return item
