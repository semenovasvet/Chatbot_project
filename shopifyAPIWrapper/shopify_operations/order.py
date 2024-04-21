from sgqlc.operation import Operation
from ..shopify_schema import QueryRoot
from . import Shopify_Operations
from .. import config


class Order(Shopify_Operations):
    def __init__(self) -> None:
        pass
        super().__init__()


    def find_discounts(self, id: str) -> dict:
        schema = Operation(QueryRoot)
        order = schema.order(id=id)
        order.id()
        line_items = order.line_items(first=10)
        a = line_items.edges.node.discount_allocations()
        a.discount_application().value()
        response = self.shopify_post(schema)
        return response