import logging
from shopifyFunctions import Shopify

class ShopifyFindOrders:
    def __init__(self, email) -> None:
        self.shopify = Shopify()
        self.email = email
        self.ordersList = []
        self.trackingLinks = {}
        self.isFound = True
    
    def main(self):
        self.find_paid_orders()
        if self.ordersList and self.isFound:
            self.find_tracking_links()
        logging.warning(f"{self.trackingLinks=}")
        return self.trackingLinks, self.isFound
    

    def find_tracking_links(self):
        for order in self.ordersList:
            fulfillments = order.get("fulfillments", [])
            if fulfillments and fulfillments[0].get("trackingInfo"):
                self.trackingLinks[order["name"]] = order["fulfillments"][0]["trackingInfo"][0].get("url")
                

    def find_paid_orders(self):
        orders = self.shopify.shopify_query("orders_query", self.email)
        if orders:
            for order in orders:
                if order["node"]["displayFinancialStatus"] in ["PAID", "PARTIALLY_PAID"]:
                    self.ordersList.append(order["node"])
        else:
            self.isFound = False