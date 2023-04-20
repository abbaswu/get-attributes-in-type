from dis import Bytecode
from enum import Enum, auto
from functools import lru_cache
from typing import Generator
from types import CodeType, FunctionType


class State(Enum):
    SELF_NOT_LOADED = auto()
    SELF_LOADED = auto()


# looks for the following two bytecode sequences
# 10 LOAD_FAST                0 (self)
# 12 LOAD_ATTR                2 (update)
# and
# 66 LOAD_FAST                0 (self)
# 68 STORE_ATTR               5 (_io_refs)
# uses the state machine design pattern
def get_attributes_accessed_on_self_in_code(code: CodeType) -> Generator[str, None, None]:
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
            if instruction.opname in ('LOAD_ATTR', 'STORE_ATTR'):
                yield instruction.argval

            state = State.SELF_NOT_LOADED


def get_dynamic_attributes_accessed_on_self_in_constructor(type: type) -> set[str]:
    # find `__init__`
    if '__init__' in type.__dict__:
        __init__ = type.__dict__['__init__']
    else:
        __init__ = None

    # only support constructors of `FunctionType` (i.e., user-defined functions)
    if isinstance(__init__, FunctionType):
        dynamic_attributes_in_type: set[str] = set(
            get_attributes_accessed_on_self_in_code(
                __init__.__code__
            )
        )

        return dynamic_attributes_in_type
    else:
        return set()


@lru_cache(maxsize=None)
def get_dynamic_attributes_in_type(type: type) -> set[str]:
    if not type.__bases__:
        return get_dynamic_attributes_accessed_on_self_in_constructor(type)
    else:
        dynamic_attributes_in_type: set[str] = set()

        for base in type.__bases__:
            dynamic_attributes_in_type.update(get_dynamic_attributes_in_type(base))

        dynamic_attributes_in_type.update(get_dynamic_attributes_accessed_on_self_in_constructor(type))

        return dynamic_attributes_in_type
