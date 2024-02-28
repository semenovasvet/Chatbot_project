import logging
from typing import Literal
from sgqlc.operation import Operation
from ..graphql_mutations.mutation import Mutation, CurrencyCode, CatalogCreateInput, CompanyLocationIds, CatalogStatus, PriceListCreatePayload, PriceListCreateInput, PriceListAdjustmentInput, PriceListAdjustmentSettingsInput, PriceListParentCreateInput, PriceListAdjustmentType, CompareAtMode, Prices, Price, CompareAtPrice
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
            context = CompanyLocationIds(
                companyLocationIds = [companyLocationId]
            )
        )
        schema = Operation(Mutation)
        schema.catalogCreate(input=catalog_input)
        response = self.shopify_post(schema)
        return response
    

    def priceList_create(self, catalogId: str, adjustment_value: float, adjustment_type: str, compareAtMode: str, currency: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        priceList_input = PriceListCreateInput(
            catalogId = catalogId,
            currency = self.find_choice(CurrencyCode, currency),
            name = f"{catalogId} priceList",
            parent = PriceListParentCreateInput(
                adjustment = PriceListAdjustmentInput(
                    type = self.find_choice(PriceListAdjustmentType, adjustment_type),
                    value = adjustment_value
                ),
                settings = PriceListAdjustmentSettingsInput(
                    compareAtMode = self.find_choice(CompareAtMode, compareAtMode)
                )
            )
        )
        schema = Operation(Mutation)
        schema.priceListCreate(input=priceList_input)
        response = self.shopify_post(schema)
        return response
   

    def priceList_delete(self, priceListId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.priceListDelete(id=priceListId)
        response = self.shopify_post(schema)
        return response
    

    def priceList_addPrices(self, priceListId: str, pricesList: list) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.priceListFixedPricesAdd(priceListId=priceListId, prices = pricesList)
        schema.priceListFixedPricesAdd.prices()
        schema.priceListFixedPricesAdd.userErrors()
        response = self.shopify_post(schema)
        return response