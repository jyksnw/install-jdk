import warnings
from enum import EnumMeta
from functools import wraps
from inspect import isclass
from inspect import isfunction
from typing import Callable
from typing import Union

from jdk.enums import BaseDetectableEnum
from jdk.enums import BaseEnum


def extend_enum(parent: BaseEnum) -> Callable[[BaseEnum], BaseEnum]:
    @wraps(parent)
    def wrapper(extended: BaseEnum) -> BaseEnum:
        joined = {}
        for item in parent:
            joined[item.name] = item.value
        for item in extended:
            joined[item.name] = item.value
        return BaseEnum(extended.__name__, joined)

    return wrapper


def extend_detectable_enum(
    parent: BaseDetectableEnum,
) -> Callable[[BaseDetectableEnum], BaseDetectableEnum]:
    @wraps(parent)
    def wrapper(extended: BaseDetectableEnum) -> BaseDetectableEnum:
        joined = {}
        for item in parent:
            joined[item.name] = item.value
        for item in extended:
            joined[item.name] = item.value
        extended_enum = BaseDetectableEnum(extended.__name__, joined)
        extended_enum.detect = extended.detect
        extended_enum.transform = extended.transform
        return extended_enum

    return wrapper


def extends(
    parent: Union[BaseEnum, BaseDetectableEnum]
) -> Callable[
    [Union[BaseEnum, BaseDetectableEnum]], Union[BaseEnum, BaseDetectableEnum]
]:
    @wraps(parent)
    def wrapper(
        extended: Union[BaseEnum, BaseDetectableEnum]
    ) -> Union[BaseEnum, BaseDetectableEnum]:
        parent_type = type(parent)
        if parent_type is EnumMeta:
            first_value = list(parent)[0]
            first_enum = parent(first_value)
            if isinstance(first_enum, BaseDetectableEnum):
                return extend_detectable_enum(parent)(extended)
            if isinstance(first_enum, BaseEnum):
                return extend_enum(parent)(extended)
        raise NotImplementedError(f"{extended.__class__.__name__} can not be extended")

    return wrapper


def deprecated(reason):
    if isinstance(reason, (str, bytes, str)):

        def decorator(func):
            msg = "Call to deprecated function {name} ({reason})"
            if isclass(func):
                msg = "Call to deprecated class {name} ({reason})"

            @wraps(func)
            def wrapper(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    msg.format(name=func.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func(*args, **kwargs)

            return wrapper

        return decorator
    elif isclass(reason) or isfunction(reason):
        _func = reason
        msg = "Call to deprecated function {name}"
        if isclass(_func):
            msg = "Call to deprecated class {name}"

        @wraps(_func)
        def wrapper(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                msg.format(name=_func.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return _func(*args, **kwargs)

        return wrapper
    else:
        raise TypeError(repr(type(reason)))
