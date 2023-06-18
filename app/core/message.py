"""
Messages for using in code
"""

"""
ERRORS
"""
ERROR_ENTITY_ENTRY_NOT_FOUND = '{entity} not found'
ERROR_ENTITY_ENTRY_ALREADY_EXISTS = '{entity} already exists.'
ERROR_INCORRECT_DATA_FORMAT = '{format} is not one of allowed formats {formats}'
ERROR_INCORRECT_SORTING = "The sorting value '{fields}' is incorrect"
ERROR_INCORRECT_SORTING_WITH_FORMAT = (
    "The sorting value '{fields}' is incorrect. "
    "The correct format is 'field_1,-field_2,another_field'"
)
ERROR_INCORRECT_SORTING_WITH_AVAILABLE = (
    "The sorting values '{fields}' are incorrect. "
    "The available values are '{available}'"
)
ERROR_ACTION_FORBIDDEN = "You don't have enough rights to do this"
ERROR_NOT_AUTHORIZED = "User is not authorized"

"""
MODELS
"""
MODEL_ORDER_TYPE = 'Order Type'
MODEL_ORDER_TYPE_PARAM = 'Order Type Param'
MODEL_ORDER = 'Order'
MODEL_ORDER_PARAM_VALUE = 'Order Param Value'
MODEL_ORDER_CONFIRMATION = 'Order Confirmation'
MODEL_USER = 'User'
MODEL_AUTH_CLIENT = 'Auth Client'
