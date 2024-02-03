# deals_finder.py


def remove_unavailable_items(all_items):
    count = 0
    for _, items in all_items.items():
        for item in items:
            if item["availability"] is False:
                items.remove(item)
                count += 1
    return all_items, count


def find_individual_best_deals(all_items):
    best_deals = []
    for seller, items_list in all_items.items():
        for item in items_list:
            # if the seller indicates a free delivery threshold and the cumulative price is greater than or equal to the threshold
            if item["free_delivery"] and item["total_price"] >= item["free_delivery"]:
                best_deals.append(item)
    return best_deals


def find_best_deals(all_items):
    # find the common sellers
    common_sellers = []
    for _, items in all_items.items():
        common_sellers.append([item["seller"] for item in items])
    common_sellers = set(common_sellers[0]).intersection(*common_sellers)

    # for each common seller find, find the cumulative price of all items sold by that seller
    # and sort the items by price
    best_deals = {}
    for seller in common_sellers:
        best_deal_items = {}
        for _, items_list in all_items.items():
            for item in items_list:
                if item["seller"] == seller:
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
        best_deals[seller] = best_deal_items

    # add the delivery price to the cumulative price if the cumulative price is less than the free delivery price threshold
    for seller, item in best_deals.items():
        # if the seller indicates a free delivery threshold and the cumulative price is greater than or equal to the threshold
        if item["free_delivery"] and item["cumulative_price"] >= item["free_delivery"]:
            item["cumulative_price_plus_delivery"] = item["cumulative_price"]
        else:
            item["cumulative_price_plus_delivery"] = (
                item["cumulative_price"] + item["delivery_price"]
            )
        best_deals[seller] = item

    # sort best deals by price
    best_deals = sorted(
        best_deals.values(), key=lambda x: x["cumulative_price_plus_delivery"]
    )

    return best_deals
