from __future__ import annotations

import os
import sys
from types import TracebackType
from typing import Callable, Optional, Set, Type, Union

from graphql import GraphQLInputObjectType, GraphQLObjectType

from strawberry.type import StrawberryType

from .exception import StrawberryException
from .invalid_argument_type import InvalidArgumentTypeError
from .invalid_union_type import InvalidTypeForUnionMergeError, InvalidUnionTypeError
from .missing_arguments_annotations import MissingArgumentsAnnotationsError
from .missing_field_annotation import MissingFieldAnnotationError
from .missing_return_annotation import MissingReturnAnnotationError
from .object_is_not_a_class import ObjectIsNotClassError
from .object_is_not_an_enum import ObjectIsNotAnEnumError
from .private_strawberry_field import PrivateStrawberryFieldError
from .scalar_already_registered import ScalarAlreadyRegisteredError


# TODO: this doesn't seem to be tested
class WrongReturnTypeForUnion(Exception):
    """The Union type cannot be resolved because it's not a field"""

    def __init__(self, field_name: str, result_type: str):
        message = (
            f'The type "{result_type}" cannot be resolved for the field "{field_name}" '
            ", are you using a strawberry.field?"
        )

        super().__init__(message)


# TODO: this doesn't seem to be tested
class UnallowedReturnTypeForUnion(Exception):
    """The return type is not in the list of Union types"""

    def __init__(
        self, field_name: str, result_type: str, allowed_types: Set[GraphQLObjectType]
    ):
        formatted_allowed_types = list(sorted(type_.name for type_ in allowed_types))

        message = (
            f'The type "{result_type}" of the field "{field_name}" '
            f'is not in the list of the types of the union: "{formatted_allowed_types}"'
        )

        super().__init__(message)


# TODO: this doesn't seem to be tested
class InvalidTypeInputForUnion(Exception):
    def __init__(self, annotation: GraphQLInputObjectType):
        message = f"Union for {annotation} is not supported because it is an Input type"
        super().__init__(message)


# TODO: this doesn't seem to be tested
class MissingTypesForGenericError(Exception):
    """Raised when a generic types was used without passing any type."""

    def __init__(self, annotation: Union[StrawberryType, type]):
        message = (
            f'The type "{repr(annotation)}" is generic, but no type has been passed'
        )

        super().__init__(message)


# TODO: this doesn't seem to be tested
class UnsupportedTypeError(Exception):
    def __init__(self, annotation):
        message = f"{annotation} conversion is not supported"

        super().__init__(message)


# TODO: this doesn't seem to be tested
class UnresolvedFieldTypeError(Exception):
    def __init__(self, field_name: str):
        message = (
            f"Could not resolve the type of '{field_name}'. Check that the class is "
            "accessible from the global module scope."
        )
        super().__init__(message)


class MultipleStrawberryArgumentsError(Exception):
    def __init__(self, argument_name: str):
        message = (
            f"Annotation for argument `{argument_name}` cannot have multiple "
            f"`strawberry.argument`s"
        )

        super().__init__(message)


class WrongNumberOfResultsReturned(Exception):
    def __init__(self, expected: int, received: int):
        message = (
            "Received wrong number of results in dataloader, "
            f"expected: {expected}, received: {received}"
        )

        super().__init__(message)


class FieldWithResolverAndDefaultValueError(Exception):
    def __init__(self, field_name: str, type_name: str):
        message = (
            f'Field "{field_name}" on type "{type_name}" cannot define a default '
            "value and a resolver."
        )

        super().__init__(message)


class FieldWithResolverAndDefaultFactoryError(Exception):
    def __init__(self, field_name: str, type_name: str):
        message = (
            f'Field "{field_name}" on type "{type_name}" cannot define a '
            "default_factory and a resolver."
        )

        super().__init__(message)


class MissingQueryError(Exception):
    def __init__(self):
        message = 'Request data is missing a "query" value'

        super().__init__(message)


class InvalidDefaultFactoryError(Exception):
    def __init__(self):
        message = "`default_factory` must be a callable that requires no arguments"

        super().__init__(message)


class InvalidCustomContext(Exception):
    """Raised when a custom context object is of the wrong python type"""

    def __init__(self):
        message = (
            "The custom context must be either a class "
            "that inherits from BaseContext or a dictionary"
        )
        super().__init__(message)


original_exception_hook = sys.excepthook

ExceptionHandler = Callable[
    [Type[BaseException], BaseException, Optional[TracebackType]], None
]


def _should_use_rich_exceptions():
    errors_disabled = os.environ.get("STRAWBERRY_DISABLE_RICH_ERRORS", "")

    return errors_disabled.lower() not in ["true", "1", "yes"]


def exception_handler(
    exception_type: Type[BaseException],
    exception: BaseException,
    traceback: Optional[TracebackType],
):
    def _get_handler() -> ExceptionHandler:
        if (
            issubclass(exception_type, StrawberryException)
            and _should_use_rich_exceptions()
        ):
            try:
                import rich
            except ImportError:
                pass
            else:

                def _handler(
                    exception_type: Type[BaseException],
                    exception: BaseException,
                    traceback: Optional[TracebackType],
                ):
                    rich.print(exception)

                return _handler

        return original_exception_hook

    _get_handler()(exception_type, exception, traceback)


sys.excepthook = exception_handler


__all__ = [
    "StrawberryException",
    "MissingArgumentsAnnotationsError",
    "MissingReturnAnnotationError",
    "WrongReturnTypeForUnion",
    "UnallowedReturnTypeForUnion",
    "ObjectIsNotAnEnumError",
    "ObjectIsNotClassError",
    "InvalidUnionTypeError",
    "InvalidTypeForUnionMergeError",
    "MissingTypesForGenericError",
    "UnsupportedTypeError",
    "UnresolvedFieldTypeError",
    "PrivateStrawberryFieldError",
    "MultipleStrawberryArgumentsError",
    "ScalarAlreadyRegisteredError",
    "WrongNumberOfResultsReturned",
    "FieldWithResolverAndDefaultValueError",
    "FieldWithResolverAndDefaultFactoryError",
    "MissingQueryError",
    "InvalidArgumentTypeError",
    "InvalidDefaultFactoryError",
    "InvalidCustomContext",
    "MissingFieldAnnotationError",
]
