class JSONResponseParsingError(Exception):
    """ Error during parsing JSON response with update cart data """


class CartUpdateError(Exception):
    """ Error during updating cart """


class NotAuthenticatedError(Exception):
    """ User tried to update cart without authentication """


class UserIsAnonymousError(Exception):
    """ User is anonymous """


class CreateShippingAddressError(Exception):
    """ Error during creating shipping address for the order """


class ShippingAddressNotProvidedError(Exception):
    """ Delivery selected but no shipping address was entered """


class ProductsQuantityError(Exception):
    """ Ordered quantity is greater than available """


class PhoneNumberAlreadyExistsError(Exception):
    """ Phone number already exists """
