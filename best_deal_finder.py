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
                    best_deal_items["delivery_price"] = item["delivery_price"]
                    best_deal_items["free_delivery"] = item["free_delivery"]
                    best_deal_items["availability"] = item["availability"]
                    best_deal_items["cumulative_price"] = (
                        best_deal_items.get("cumulative_price", 0) + item["price"]
                    )
        best_deals[seller] = best_deal_items

    # sort best deals by price
    best_deals = sorted(best_deals.values(), key=lambda x: x["cumulative_price"])

    return best_deals
