from sgqlc.types import Type, Field, list_of, non_null, Input
from ..graphql_query.product import Metafield
from . import UserError


class MetafieldsSetPayload(Type):
    metafields = list_of(Metafield)
    userErrors = list_of(UserError)

class MetafieldDeletePayload(Type):
    deletedId = str
    userErrors = list_of(UserError)

class MetafieldsSetInput(Input):
    key = str
    namespace = str
    owner_id = str
    type = str
    value = str

class MetafieldDeleteInput(Input):
    id = str

# class Mutation(Type):
#     metafieldsSet = Field(MetafieldsSetPayload, args={'metafields': non_null(MetafieldsSetInput)})
#     metafieldDelete = Field(MetafieldDeletePayload, args={"input": non_null(MetafieldDeleteInput)})