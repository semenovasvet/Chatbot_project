import logging
from enum import Enum
from typing import Literal
from sgqlc.operation import Operation
from ..shopify_schema import Mutation, deliveryProfileUpdatePayload, DeliveryProfileInput
from . import Shopify_Operations
from .. import config


class DeliveryProfile(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()


    def deliveryProfile_update(self, variants_to_associate: list = [], variants_to_dissociate: list = [], delivery_profile_id: str = config.SHIPMENT_7_12_DAYS):
        """create schema input, create schema with this input -> send to shopify"""

        delivery_profile_input = DeliveryProfileInput(
            variants_to_associate = variants_to_associate,
            variants_to_dissociate = variants_to_dissociate
        )
        schema = Operation(Mutation)
        schema.delivery_profile_update(id=delivery_profile_id, profile=delivery_profile_input)
        response = self.shopify_post(schema)
        return response