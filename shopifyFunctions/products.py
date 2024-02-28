import logging
import pandas as pd
from . import Shopify


class ShopifyExport:
    def __init__(self) -> None:
        self.shopify = Shopify()
        self.dataframe = pd.DataFrame(columns=["id","title", "body", "type", "price", "endpoint"])
    
    def iterator(self):
        end = False
        counter = 0
        cursor = None
        while not end and counter < 50:
            variables = {"numProducts": 50,"cursor": cursor}
            productPage = self.shopify.graphql_shopify("products_iterator", variables=variables)
            if productPage:
                if productPage["products"]["nodes"]:
                    self.extract_data(productPage["products"]["nodes"])
                    if productPage["products"]["pageInfo"]["hasNextPage"]:
                        cursor = productPage["products"]["pageInfo"]["endCursor"]
                    else:
                        end = True
            counter += 1
        self.dataframe.to_csv("productData.csv")


    def extract_data(self, products_list: list):
        for item in products_list:
            price = self.find_price(item["variants"]["nodes"])
            if price and item["status"]=="ACTIVE":
                new_row = {"id": item["id"], "title": item["title"], "body": item["bodyHtml"], "type": item["productType"], "price": price, "endpoint": item["handle"]}
                self.dataframe = pd.concat([self.dataframe, pd.DataFrame([new_row])], ignore_index=True)
        
    
    def find_price(self, variants: list):
        prices = []
        for variant in variants:
            if variant["price"]:
                prices.append(float(variant["price"]))
        if prices:
            return min(prices)
