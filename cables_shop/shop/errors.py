class JSONResponseParsingError(Exception):
    """Error during parsing JSON response with update cart data"""


class CartUpdateError(Exception):
    """Error during updating cart"""


class CustomerInfoUpdateError(Exception):
    """Error during updating customer information"""


class NotEnoughProductsInStockError(Exception):
    """Error during updating quantity in stock"""
