import logging
from typing import Literal
from sgqlc.operation import Operation
# from util.shopifyFunctions.graphql_mutations.metafield import MetafieldsSetInput, MetafieldDeleteInput
from ..graphql_mutations.mutation import Mutation, MetafieldsSetInput, MetafieldDeleteInput
from ..graphql_query.query import Query
from ..config import Metafield_Key
from . import Shopify_Operations
from .. import config


class Metafield(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()


    def metafield_update(self, owner_id: str, value: str, metafield_key: str) -> dict:
        """ create schema input, create a schema with input in it -> send to shopify"""
        if metafield_key == Metafield_Key.VARIANT_DISCOUNT.value or metafield_key == Metafield_Key.PRODUCT_DISCOUNT.value:
            metafield_type = config.TYPE_JSON
        
        elif metafield_key in [Metafield_Key.ORDER_LIST_VARIANTS.value, Metafield_Key.ORDER_LIST_VARIANTS_2.value, Metafield_Key.ORDER_LIST_PRODUCTS.value]:
            metafield_type = config.TYPE_LIST_VARIANTS
        
        metafields_input = MetafieldsSetInput(
        key=metafield_key,
        namespace=config.NAMESPACE_CUSTOM,
        owner_id=owner_id,
        type=metafield_type,
        value=value
        )
        schema = Operation(Mutation)
        schema.metafieldsSet(metafields=metafields_input)
        response = self.shopify_post(schema)
        return response
    

    def metafield_delete(self, variantId: str, metafield_key: str) -> dict:
        """ query metafield key for this variant -> if metafield is found, use its id to delete it in shopify (make it empty)"""
        metafield_id = None
        query_schema = Operation(Query)
        query_schema_product = query_schema.productVariant(id=variantId)
        query_schema_product.metafield(key=metafield_key)

        query_response = self.shopify_post(query_schema)
        if query_response and query_response.get("productVariant", None) and query_response["productVariant"].get("metafield", None):
            metafield_id = query_response["productVariant"]["metafield"]["id"]
        if metafield_id:
            id_to_delete = MetafieldDeleteInput(
                id=metafield_id
            )
            schema = Operation(Mutation)
            schema.metafieldDelete(input=id_to_delete)
            response = self.shopify_post(schema)
            return response
        else:
            return {"Metafield_is_empty": True}