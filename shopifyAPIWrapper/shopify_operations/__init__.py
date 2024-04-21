from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation
import os
from sgqlc.types import EnumMeta
from .. import config
from dotenv import load_dotenv

load_dotenv()


class Shopify_Operations:
    def __init__(self) -> None:
        print(os.environ["shopifyAccessToken"])
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": os.environ["shopifyAccessToken"]
        }


    def shopify_post(self, schema: Operation) -> dict:
        """sends information to shopify in graphQl"""

        endpoint = HTTPEndpoint(url=f'{config.SHOPIFY_URL}graphql.json', base_headers=self.headers, method="POST")
        response = endpoint(schema)
        if "data" in response and "errors" not in response:
            return response["data"]
        elif "errors" in response:
            return response["errors"]
        return response
    
    
    @staticmethod
    def find_choice(look_in: EnumMeta, choice: str):
        if type(look_in) is not EnumMeta:
            raise ValueError("look_in must be an Enum")
        for c in look_in.__choices__:
            if c == choice:
                return c
        raise ValueError(f"Invalid choice: {choice}")