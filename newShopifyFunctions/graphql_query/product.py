from sgqlc.types import Type, Field, list_of
from sgqlc.types.datetime import DateTime
from sgqlc.types.relay import Connection, connection_args


class Metafield(Type):
    id = str
    namespace = str
    key = str
    value = str
    created_at = DateTime
    updated_at = DateTime

class Product(Type):
    id = str
    title = str

class ProductConnection(Connection):
    nodes = list_of(Product)
