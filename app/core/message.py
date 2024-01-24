"""
Messages for using in code
"""

"""
ERRORS
"""
ERROR_ENTITY_ENTRY_NOT_FOUND = "{entity} не найдено"
ERROR_ENTITY_ENTRY_ALREADY_EXISTS = "{entity} уже создан."
ERROR_INCORRECT_DATA_FORMAT = (
    "{format} не является одним из разрешенных форматов - {formats}"
)
ERROR_INCORRECT_SORTING = "Поле сортировки '{fields}' не поддерживается"
ERROR_INCORRECT_SORTING_WITH_FORMAT = (
    "Формат сортировки '{fields}' не поддерживается. "
    "Верный формат - 'field_1,-field_2,another_field'"
)
ERROR_INCORRECT_SORTING_WITH_AVAILABLE = (
    "Поле сортировки '{fields}' не поддерживается. "
    "Поддерживаемые форматы - '{available}'"
)
ERROR_ACTION_FORBIDDEN = "Недостаточно прав"
ERROR_NOT_AUTHORIZED = "Пользователь не прошел аутентификацию"
ERROR_NO_PARENT_ORDER = "Заполните родительский заказ"
ERROR_ORDER_WITH_TYPE_EXISTS = "Заявка с таким типом уже была создана"

"""
MODELS
"""
MODEL_ORDER_TYPE = "Тип заказа"
MODEL_ORDER_TYPE_PARAM = "Параметр типа заказа"
MODEL_ORDER = "Заказ"
MODEL_ORDER_PARAM_VALUE = "Значение параметра заказа"
MODEL_ORDER_STATUS = "Изменение статуса заказа"
MODEL_USER = "Пользователь"
MODEL_AUTH_CLIENT = "Клиент keycloak"
MODEL_ROLE = "Роль"
MODEL_MATERIAL = "Материал"
