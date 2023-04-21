from dis import Bytecode
from enum import Enum, auto
from functools import lru_cache
from typing import Generator
from types import CodeType, FunctionType, MethodType


class State(Enum):
    SELF_NOT_LOADED = auto()
    SELF_LOADED = auto()


# looks for the following three bytecode sequences
# 10 LOAD_FAST                0 (self)
# 12 LOAD_ATTR                2 (update)
# and
# 66 LOAD_FAST                0 (self)
# 68 STORE_ATTR               5 (_io_refs)
# and
# 0 LOAD_FAST                0 (self)
# 2 LOAD_METHOD              0 (parse)
# uses the state machine design pattern
def get_attributes_accessed_on_self_in_method_code(code: CodeType) -> Generator[str, None, None]:
    state = State.SELF_NOT_LOADED

    for instruction in Bytecode(code):
        if state == State.SELF_NOT_LOADED:
            # Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='self', argrepr='self', offset=66, starts_line=None, is_jump_target=False)
            if instruction.opname == 'LOAD_FAST' and instruction.arg == 0:
                state = State.SELF_LOADED
            else:
                state = State.SELF_NOT_LOADED
        elif state == State.SELF_LOADED:
            # Instruction(opname='LOAD_ATTR', opcode=106, arg=2, argval='update', argrepr='update', offset=12, starts_line=None, is_jump_target=False)
            # Instruction(opname='STORE_ATTR', opcode=95, arg=5, argval='_io_refs', argrepr='_io_refs', offset=68, starts_line=None, is_jump_target=False)
            # Instruction(opname='LOAD_METHOD', opcode=160, arg=0, argval='parse', argrepr='parse', offset=2, starts_line=None, is_jump_target=False)
            if instruction.opname in ('LOAD_ATTR', 'STORE_ATTR', 'LOAD_METHOD'):
                yield instruction.argval

            state = State.SELF_NOT_LOADED


def get_dynamic_attributes_accessed_on_self_in_methods(type: type) -> set[str]:
    dynamic_attributes_in_type: set[str] = set()

    for key, value in type.__dict__.items():
        # only support methods of `FunctionType` (i.e., user-defined non-`classmethod`, non-`staticmethod` methods)
        # https://medium.com/solomons-tech-stack/python3-how-to-inspect-a-functions-type-9999eeb31c0b
        if isinstance(value, FunctionType):
            dynamic_attributes_in_type.update(
                get_attributes_accessed_on_self_in_method_code(
                    value.__code__
                )
            )
        else:
            pass

    return dynamic_attributes_in_type


@lru_cache(maxsize=None)
def get_dynamic_attributes_in_type(type: type) -> set[str]:
    if not type.__bases__:
        return get_dynamic_attributes_accessed_on_self_in_methods(type)
    else:
        dynamic_attributes_in_type: set[str] = set()

        for base in type.__bases__:
            dynamic_attributes_in_type.update(get_dynamic_attributes_in_type(base))

        dynamic_attributes_in_type.update(get_dynamic_attributes_accessed_on_self_in_methods(type))

        return dynamic_attributes_in_type
