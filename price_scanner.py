# pricescanner.py

import re
import time
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService


def download_html(url, wait=5, headless=True):
    html_content = None
    try:
        # Set up Chrome options for headless browsing
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")

        # Use webdriver_manager to automatically download and manage ChromeDriver
        with webdriver.Chrome(
            service=ChromeService(), options=chrome_options
        ) as driver:
            # Navigate to the URL
            driver.get(url)

            # Wait for the page to load (adjust the sleep duration as needed)
            driver.implicitly_wait(5)

            # Get the HTML content
            html_content = driver.page_source
            # wait seconds before next URL
            time.sleep(wait)
    except Exception as e:
        raise (f"Error downloading HTML content: {e}")

    return html_content


def extract_prices_plus_shipping(html_content, quantity=1):
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
            # merchant_rating = element.xpath('div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/')[0].text.strip() TODO
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
            # convert item values to the appropriate data types
            item = _convert_data_types(
                merchant,
                merchant_reviews,
                price,
                quantity,
                delivery_price,
                free_delivery,
                availability,
            )
            results.append(item)
    except Exception as e:
        raise (f"Error extracting prices: {e}")

    return item_name, results


# TODO
def extract_best_price_shipping_included(html_content, quantity=1):
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
        # merchant_rating = element.xpath('div[@class="item_info"]/div[@class="item_merchant"]/div[@class="wrap_merchant_reviews"]/')[0].text.strip() TODO
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
        # convert item values to the appropriate data types
        item = _convert_data_types(
            merchant,
            merchant_reviews,
            price,
            quantity,
            delivery_price,
            free_delivery,
            availability,
        )
    except Exception as e:
        raise (f"Error extracting prices: {e}")

    return item_name, item


def _convert_data_types(
    merchant,
    merchant_reviews,
    price,
    quantity,
    delivery_price,
    free_delivery,
    availability,
):
    number_pattern = re.compile(r"\b\d+[,.]?\d*\b")
    item = {}

    item["seller"] = merchant
    merchant_reviews = number_pattern.search(merchant_reviews).group()
    item["seller_reviews"] = int(merchant_reviews.replace(".", ""))
    price = number_pattern.search(price).group()
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

    return item
