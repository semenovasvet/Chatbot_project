from sgqlc.types import Type, Field, list_of, non_null, Input, Enum
from ..graphql_query.catalog import Catalog
from . import UserError


class CatalogCreatePayload(Type):
    catalog = list_of(Catalog)
    userErrors = list_of(UserError)


class CompanyLocationIds(Input):
    companyLocationIds = list_of(str)

class CatalogStatus(Enum):
    __choices__ = ('ACTIVE', 'ARCHIVED', 'DRAFT')

class CatalogCreateInput(Input):
    context = Field(CompanyLocationIds)
    status = CatalogStatus
    title = str


# class Mutation(Type):
#     catalogCreate = Field(CatalogCreatePayload, args={"input": non_null(CatalogCreateInput)})