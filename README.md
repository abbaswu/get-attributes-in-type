# Get Attributes in Type

Code that gets the set of attributes in a Python `type` object (i.e., a Python class). This includes:

- Non-dynamic attributes (attributes that are not initialized in `__init__`, such as methods, class variables, and attributes defined in `__slots__`).
- Dynamic attributes (attributes initialized in the `__init__` method for classes implemented in Python). Implemented by checking the bytecode for the `__init__` method and looking for `LOAD_ATTR` and `STORE_ATTR` operations after `LOAD_FAST                0 (self)`.

The main entry point function is `get_attributes_in_type` in `get_attributes_in_type.py`. This function accepts `type: type` as a parameter and returns a `set[str]` containing the attributes within that type.
