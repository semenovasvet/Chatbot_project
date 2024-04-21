import logging
import pandas as pd
from shopifyAPIWrapper.shopify_operations.query import QueryShopify


class ShopifyExport:
    """
    Handles the export of product information from Shopify into a local DataFrame.

    This class utilises Shopify's API to fetch product variant details and compiles
    them into a pandas DataFrame with specified columns for further analysis or export.

    """
    def __init__(self) -> None:
        """ Setting up necessary attributes.
        Attributes:
            query (QueryShopify): An instance of the QueryShopify class for querying Shopify data.
            dataframe (pd.DataFrame): A DataFrame to store product data with columns:
                                  ['id', 'title', 'body', 'type', 'price', 'endpoint'].
        """
        self.query = QueryShopify()
        self.dataframe = pd.DataFrame(columns=["id","title", "body", "type", "price", "endpoint"])


    def main(self) -> None:
        """
        Main function: utilises iterator function to fetch product data from shopify. 
        Each 'product_var' value is a dictionary.
        """
        try:
            for product_var in self.query.product_variants_iterator():
                if product_var:
                    self.extract_data(product_var)
            self.dataframe.to_csv("productData.csv")

        except Exception as e:
            logging.error(f"An error occured during product iteration: {e}")


    def extract_data(self, product_var: dict) -> None:
        """
        Extracts data from a single product variant dictionary and appends it to the DataFrame.

        Parameters:
            product_var (dict): A dictionary containing details of a Shopify product variant.

        Processes individual product variant data, checking for price and availability, 
        and appends valid data as a new row to the DataFrame.
        """
        try:
            price = product_var["price"]
            availability = product_var["availableForSale"]
            if price and availability:
                var_title = product_var["title"]
                title = f'{product_var["product"]["title"]}: {var_title}' if var_title != "Default Title" else product_var["product"]["title"]
                new_row = {"id": product_var["id"], 
                           "title": title, 
                           "body": product_var["product"]["descriptionHtml"], 
                           "type": product_var["product"]["productType"], 
                           "price": price, 
                           "endpoint": product_var["product"]["handle"]}
                logging.warning(new_row)
                self.dataframe = pd.concat([self.dataframe, pd.DataFrame([new_row])], ignore_index=True)

        except Exception as e:
            logging.error(f"An error occured while processing and saving data to the local database {e}")


