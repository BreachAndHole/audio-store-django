class JSONResponseParsingError(Exception):
    """ Error during parsing JSON response with update cart data """


class CartUpdateError(Exception):
    """ Error during updating cart """


class UserIsAnonymousError(Exception):
    """ User is anonymous """


class CreateShippingAddressError(Exception):
    """ Error during creating shipping address for the order"""


class ProductsQuantityError(Exception):
    """ Ordered quantity is greater than available """
