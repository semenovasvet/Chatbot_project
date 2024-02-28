from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args


class Adjustment(Type):
    type: str
    value = float


class compareAtMode(Type):
    compareAtMode = str


class Parent(Type):
    adjustment = Field(Adjustment)
    settings = Field(compareAtMode)


class PriceList(Type):
   id = str
   fixedPricesCount = int
   name = str
   parent = Field(Parent)


class Catalog(Type):
  id = str
  title = str
  status = str
  priceList = Field(PriceList)


class CatalogConnection(Connection):
   nodes = list_of(Catalog)
        
