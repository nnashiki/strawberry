from typing import TYPE_CHECKING

from .exception import StrawberryException
from .exception_source.exception_source_is_argument import ExceptionSourceIsArgument


if TYPE_CHECKING:
    from strawberry.types.fields.resolver import StrawberryResolver


# TODO: can we find a better name? Maybe invalid argument on resolver
class InvalidFieldArgumentError(ExceptionSourceIsArgument, StrawberryException):
    documentation_url = "https://errors.strawberry.rocks/invalid-field-argument"

    def __init__(
        self,
        resolver: "StrawberryResolver",
        argument_name: str,
        argument_type: str,
    ):
        self.resolver = resolver
        self.argument_name = argument_name

        self.message = (
            f'Argument "{argument_name}" on field "{resolver.name}" cannot be of type '
            f'"{argument_type}"'
        )
        self.rich_message = self.message
        self.suggestion = "Well..."
        self.annotation_message = (
            f'Argument "{argument_name}" cannot be of type "{argument_type}"'
        )
