from locale import currency
from sgqlc.types import Type, Field, list_of, non_null, Input, Enum
from ..graphql_query.catalog import PriceList
from . import UserError, CurrencyCode


class PriceListAdjustmentType(Enum):
    __choices__ = ('PERCENTAGE_DECREASE', 'PERCENTAGE_INCREASE')


class CompareAtMode(Enum):
    __choices__ = ('ADJUSTED', 'NULLIFY')

############################################################################################################
class PriceListAdjustmentInput(Input):
    type = PriceListAdjustmentType
    value = float


class PriceListAdjustmentSettingsInput(Input):
    compareAtMode = CompareAtMode


class PriceListParentCreateInput(Input):
    adjustment = Field(PriceListAdjustmentInput)
    settings = Field(PriceListAdjustmentSettingsInput)


class PriceListCreateInput(Input):
    catalogId = str
    currency = CurrencyCode
    name = str
    parent = PriceListParentCreateInput

############################################################################################################
class PriceListDeleteInput(Input):
    id = str

############################################################################################################
class Price(Input):
    amount = float
    currencyCode = CurrencyCode

class CompareAtPrice(Input):
    amount = float
    currencyCode = CurrencyCode

class Prices(Input):
    compareAtPrice = Field(CompareAtPrice)
    price = Field(Price)
    variantId = str

class PriceOutput(Type):
    amount = float
    currencyCode = CurrencyCode

class PricesOutput(Type):
    compareAtPrice = Field(PriceOutput)
    price = Field(PriceOutput)

# class PriceListPriceInput(Input):
#     prices = list_of(Prices)


############################################################################################################
class PriceListDeletePayload(Type):
    deletedId = str
    userErrors = list_of(UserError)


class PriceListCreatePayload(Type):
    priceList = Field(PriceList)
    userErrors = list_of(UserError)


class PriceListAddFixedPricesPayload(Type):
    prices = list_of(PricesOutput)
    userErrors = list_of(UserError)