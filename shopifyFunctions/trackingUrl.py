import logging
import datetime
from typing import Tuple
from newShopifyFunctions.shopify_operations.query import QueryShopify


class ShopifyTracking:
    def __init__(self) -> None:
        self.query = QueryShopify()
        self.date = str((datetime.datetime.now() - datetime.timedelta(days=90)).date())
    

    def find_by_number(self, salesOrderNumber: str) -> dict:
        order = self.query.query_orders(query=f"name:{salesOrderNumber} AND updated_at:>2023-10-01")
        if order:
            if order["fulfillments"]:
                url_list = []
                for trackingInfo in order["fulfillments"]:
                    if trackingInfo["trackingInfo"]:
                        url_list.append(trackingInfo["trackingInfo"][0]["url"])
                if url_list:
                    return {"order": True, "shipment": True, "urls": url_list}

            return {"order": True, "shipment": False, "url": None}
        else:
            logging.warning("order was not found")
            return {"order": False, "shipment": False, "url": None}
    

    def find_by_email(self, email: str) -> Tuple[dict, bool]:
        trackingLinks = {}
        orders = QueryShopify().query_orders(f"email:{email} AND (financial_status:PAID OR financial_status:PARTIALLY_PAID) AND updated_at:>{self.date}")
        if orders:
            for order in orders:
                if order["fulfillments"] and order["fulfillments"][0]["trackingInfo"]:
                    trackingLinks[order["name"]] = (order["fulfillments"][0]["trackingInfo"][0]["url"])
            logging.warning(f"{trackingLinks=}")
            return trackingLinks, True
        return trackingLinks, False