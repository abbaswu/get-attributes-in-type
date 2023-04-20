def get_non_dynamic_attributes_in_type(type: type) -> set[str]:
    return set(dir(type))
