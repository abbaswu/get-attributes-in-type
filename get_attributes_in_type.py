from functools import lru_cache

from get_dynamic_attributes_in_type import get_dynamic_attributes_in_type
from get_non_dynamic_attributes_in_type import get_non_dynamic_attributes_in_type


@lru_cache(maxsize=None)
def get_attributes_in_type(type: type) -> set[str]:
    return get_non_dynamic_attributes_in_type(type) | get_dynamic_attributes_in_type(type)
