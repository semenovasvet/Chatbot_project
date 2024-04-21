import logging
import datetime
from typing import Tuple
from shopifyAPIWrapper.shopify_operations.query import QueryShopify
from . import config


class ShopifyTracking:
    """ Handles interactions with the Shopify server to retrieve order information."""

    def __init__(self) -> None:
        """ Setting up necessary attributes.
        Attributes:
            query (QueryShopify): An instance of the QueryShopify class for querying Shopify data.
            date (str): The starting date from which orders will be searched, formatted as a string.
        """
        self.query = QueryShopify()
        self.date = str((datetime.datetime.now() - datetime.timedelta(days=config.SEARCH_TIMEFRAME)).date())
    

    def find_by_number(self, salesOrderNumber: str) -> dict:
        """
        Fetches order details based on the sales order number.

        Parameters:
            salesOrderNumber (str): The sales order number to query.

        Returns:
            dict: A dictionary with information about the order, structured in the following way:
                {
                    "order": bool (True if the order was found, False otherwise),
                    "shipment": bool (True if shipment exists, False otherwise),
                    "urls": list[urls]
                }
        """
        try:
           # filter orders by sales order number, including only those placed after the Shopify launch date to avoid duplicates from orders made on previous systems
            orders = self.query.query_orders(query=f"name:{salesOrderNumber} AND updated_at:>{config.SHOPIFY_LAUNCH_DATE}")
            if orders and len(orders) == 1:
                order = orders[0]
                if order.get("fulfillments", None):
                    url_list = [info['trackingInfo'][0]['url'] for info in order['fulfillments'] if 'trackingInfo' in info]
                    if url_list:
                        return {"order": True, "shipment": True, "urls": url_list}
                    return {"order": True, "shipment": False, "urls": None}
                
            logging.warning("order was not found")
            return {"order": False, "shipment": False, "urls": None}
        
        except Exception as e:
            logging.error(f"An error occured while searching sales order by order number {salesOrderNumber} in Shopify: {str(e)}")
            return {"order": False, "shipment": False, "urls": None}
    

    def find_by_email(self, email: str) -> Tuple[dict, bool]:
        """
        Fetches all orders associated with the given email that are either paid or partially paid.

        Parameters:
            email (str): Customer's email.

        Returns:
            Tuple[dict, bool]: A tuple containing:
                - A dictionary of order names and their tracking URLs: {'orderNumber': url}
                - A boolean indicating if any orders were found
        """
        trackingLinks = {}
        try:
            orders = self.query.query_orders(f"email:{email} AND (financial_status:PAID OR financial_status:PARTIALLY_PAID) AND updated_at:>{self.date}")
            if orders:
                for order in orders:
                    if 'fulfillments' in order and order['fulfillments'] and 'trackingInfo' in order['fulfillments'][0]:
                        trackingLinks[order["name"]] = order['fulfillments'][0]['trackingInfo'][0]['url']
            
        except Exception as e:
            logging.error(f"An error occured while searching sales order by email {email} in Shopify: {str(e)}")

        return trackingLinks, bool(trackingLinks)