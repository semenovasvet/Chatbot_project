from sgqlc.types import Type, Field, list_of
from .catalog import Catalog, CatalogConnection
from .company import Company, CompanyLocation, CompanyLocationConnection, Customer, CustomerConnection
from .product import Product, ProductConnection
from .order import Order, OrderConnection


class Query(Type):
    catalog = Field(Catalog, args={"id": str})
    catalogs = Field(CatalogConnection, args={"first": int, "query": str})

    company = Field(Company, args={"id": str})
    companyLocation = Field(CompanyLocation, args={"id": str})
    companyLocations = Field(CompanyLocationConnection, args={"first": int, "query": str})

    customer = Field(Customer, args={"id": str})
    customers = Field(CustomerConnection, args={"first": int, "query": str})

    product = Field(Product, args={"id": str})
    products = Field(ProductConnection, args={"first": int, "query": str})
    products_iterator = Field(ProductConnection, args={"first": int, "query": str, "after": str})
    productVariant = Field(Product, args={"id": str})
    productVariants = Field(ProductConnection, args={"first": int, "query": str})

    order = Field(Order, args={"id": str})
    orders = Field(OrderConnection, args={"first": int, "query": str})