import logging
from enum import Enum
from typing import Optional, List, Generator
from sgqlc.operation import Operation
from ..shopify_schema import QueryRoot
from . import Shopify_Operations
from .. import config


class QueryShopify(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()


    def query_shopify(self, entityName: str, **kwargs) -> Optional[dict]:
        schema = Operation(QueryRoot)
        query_method = getattr(schema, entityName)
        query_method(**kwargs)
        response = self.shopify_post(schema)
        if entityName in response and response[entityName].get("nodes", None):
            return response[entityName]["nodes"]
        elif entityName in response:
            return response[entityName]
        else:
            logging.error(f"Error while trying to query {entityName}. Response: {response}")
    

    def query_order(self, id: str) -> Optional[dict]:
        schema = Operation(QueryRoot)
        order = schema.order(id=id)
        order.id()
        order.name()
        line_item = order.line_items(first=50)
        line_item.nodes.id()
        line_item.nodes.sku()
        discount_allocations = line_item.nodes.discount_allocations()
        discount_allocations.discount_application()
        discount_allocations.allocated_amount_set()

        line_item.nodes.discounted_total_set()
        discount_applications = order.discount_applications(first=50)
        shipping_lines = order.shipping_lines(first=50)
        shipping_lines.nodes.discount_allocations()
        shipping_lines.nodes.discounted_price_set()
        shipping_lines.nodes.original_price_set()
        discount_applications.nodes.allocation_method()
        discount_applications.nodes.index()
        discount_applications.nodes.target_selection()
        discount_applications.nodes.target_type()
        discount_applications.nodes.value() 
        order.additional_fees()
        order.cart_discount_amount_set()
        order.current_cart_discount_amount_set()
        order.current_subtotal_line_items_quantity()
        order.current_subtotal_price_set()
        order.current_total_discounts_set()
        order.current_total_price_set()
        order.discount_codes()

        response = self.shopify_post(schema)
        if response.get("order", None):
            return response["order"]
        logging.error(f"Error in query_order by id: {response}")
        return None
    

    def query_orders(self, query: str) -> Optional[List[dict]]:
        schema = Operation(QueryRoot)
        orders = schema.orders(first=50, query=query)
        orders.nodes.id()
        orders.nodes.name()
        orders.nodes.email()
        orders.nodes.display_financial_status()
        orders.nodes.fulfillments(first=50)
        response = self.shopify_post(schema)
        if response["orders"]["nodes"] and len(response["orders"]["nodes"]) < 50:
            return response["orders"]["nodes"]
        else:
            logging.warning("too many")
            return None
    
    
    def product_variants_iterator(self, query: str = "", next_cursor: str = None) -> Generator[dict, None, None]:
        """Iterates through all product variants and yields them
        Args:
            query (str): The query to filter the product variants. If left empty: returns all product variants. If query was unsuccessful, returns an empty list
            next_cursor (str): The cursor to get the next page of product variants"""
        
        hasNextPage = True

        while hasNextPage:
            try:
                schema = Operation(QueryRoot)
                productVariants = schema.product_variants(first=50, query=query, after=next_cursor)
                productVariants.nodes.id()
                productVariants.nodes.title()
                productVariants.nodes.sku()
                productVariants.nodes.price()
                productVariants.nodes.available_for_sale()
                productVariants.nodes.inventory_quantity()
                product = productVariants.nodes.product()
                product.title()
                product.description()
                product.description_html()
                product.product_type()
                product.handle()
                productVariants.page_info()
                response = self.shopify_post(schema)
                if "productVariants" in response:
                    list_of_variants = response["productVariants"]["nodes"]
                    logging.warning(f"-----Iterating through {len(list_of_variants)} variants-----")
                    for variant in list_of_variants:
                        yield variant
                    hasNextPage = response["productVariants"]["pageInfo"]["hasNextPage"]
                    if hasNextPage:
                        next_cursor = response["productVariants"]["pageInfo"]["endCursor"]
                    else:
                        logging.warning("No more pages to iterate")
            except Exception as error:
                logging.error(f"Error in product_variants_iterator: {error}")
                break
    

    def query_customers(self, query: str) -> Optional[List[dict]]:
        schema = Operation(QueryRoot)
        customers = schema.customers(first=50, query=query)
        customers.nodes.id()
        customers.nodes.first_name()
        customers.nodes.last_name()
        customers.nodes.email()
        customers.nodes.email_marketing_consent()
        customers.nodes.phone()
        customers.nodes.created_at()
        customers.nodes.updated_at()
        customers.nodes.verified_email()
        customers.nodes.valid_email_address()
        customers.nodes.tags()
        customers.nodes.lifetime_duration()
        customers.nodes.addresses()
        customers.nodes.company_contact_profiles()
        response = self.shopify_post(schema)
        if "customers" in response and response["customers"].get("nodes", None) and len(response["customers"]["nodes"]) < 50:
            return response["customers"]["nodes"]
        return []

