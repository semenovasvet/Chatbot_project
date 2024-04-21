import logging
from typing import Literal
from sgqlc.operation import Operation
from ..shopify_schema import Mutation, CurrencyCode, CatalogCreateInput, CatalogContextInput, CatalogStatus, PriceListCreateInput, PriceListAdjustmentInput, PriceListAdjustmentSettingsInput, PriceListParentCreateInput, PriceListAdjustmentType, PriceListCompareAtMode
from . import Shopify_Operations
from .. import config


class Catalog(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()


    def catalog_create(self, title: str, companyLocationId: str, catalogStatus: Literal['ACTIVE', 'ARCHIVED', 'DRAFT'] = "ACTIVE") -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        catalog_input = CatalogCreateInput(
            status = self.find_choice(CatalogStatus, str(catalogStatus)),
            title = title,
            context = CatalogContextInput(
                company_location_ids = [companyLocationId]
            )
        )
        schema = Operation(Mutation)
        schema.catalog_create(input=catalog_input)
        response = self.shopify_post(schema)
        return response
    

    def priceList_create(self, catalogId: str, adjustment_value: float, adjustment_type: str, compareAtMode: str, currency: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        priceList_input = PriceListCreateInput(
            catalog_id = catalogId,
            currency = self.find_choice(CurrencyCode, currency),
            name = f"{catalogId} priceList",
            parent = PriceListParentCreateInput(
                adjustment = PriceListAdjustmentInput(
                    type = self.find_choice(PriceListAdjustmentType, adjustment_type),
                    value = adjustment_value
                ),
                settings = PriceListAdjustmentSettingsInput(
                    compare_at_mode = self.find_choice(PriceListCompareAtMode, compareAtMode)
                )
            )
        )
        schema = Operation(Mutation)
        schema.price_list_create(input=priceList_input)
        response = self.shopify_post(schema)
        return response
   

    def priceList_delete(self, priceListId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.price_list_delete(id=priceListId)
        response = self.shopify_post(schema)
        return response
    

    def priceList_addPrices(self, priceListId: str, pricesList: list) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.price_list_fixed_prices_add(price_list_id=priceListId, prices = pricesList)
        schema.price_list_fixed_prices_add.prices()
        schema.price_list_fixed_prices_add.user_errors()
        response = self.shopify_post(schema)
        return response