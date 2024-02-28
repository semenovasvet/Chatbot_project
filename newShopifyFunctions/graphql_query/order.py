from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args



class TrackingInfo(Type):
    url = str
    number = str


class Fulfillment(Type):
   trackingInfo = Field(TrackingInfo, args=connection_args())


class Order(Type):
  id = str
  name = str
  email = str
  displayFinancialStatus = str
  fulfillments = Field(Fulfillment, args=connection_args())


class OrderConnection(Connection):
   nodes = list_of(Order)
   