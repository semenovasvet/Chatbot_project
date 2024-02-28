from sgqlc.types import Type, Field, list_of, non_null, Input, Enum


class UserError(Type):
    field = list_of(str)
    message = str

class CurrencyCode(Enum):
    __choices__ = ("EUR")

class CountryCode(Enum):
    __choices__ = (
        "BE", 
        "BG", 
        "CH", 
        "CA", 
        "DK", 
        "DE", 
        "EE", 
        "FI", 
        "FR", 
        "GR", 
        "GB", 
        "IE", 
        "IT", 
        "HR", 
        "LV", 
        "LT", 
        "LU", 
        "MT", 
        "NL", 
        "AT", 
        "PL", 
        "RO", 
        "SE", 
        "SK",
        "SI", 
        "ES", 
        "CZ", 
        "HU", 
        "CY"
    )