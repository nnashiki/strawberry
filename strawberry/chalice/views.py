import json
from typing import Dict, Optional, Type

from chalice.app import BadRequestError, Request, Response
from strawberry.exceptions import MissingQueryError
from strawberry.http import (
    GraphQLHTTPResponse,
    parse_query_params,
    parse_request_data,
    process_result,
)
from strawberry.http.json_dumps_params import JSONDumpsParams
from strawberry.schema import BaseSchema
from strawberry.types import ExecutionResult
from strawberry.utils.graphiql import get_graphiql_html


class GraphQLView:
    def __init__(
        self,
        schema: BaseSchema,
        render_graphiql: bool = True,
        json_encoder: Type[json.JSONEncoder] = json.JSONEncoder,
        json_dumps_params: Optional[JSONDumpsParams] = None,
        **kwargs
    ):
        self.graphiql = render_graphiql
        self._schema = schema
        self.json_encoder = json_encoder
        self.json_dumps_params = json_dumps_params or {}

    @staticmethod
    def render_graphiql() -> str:
        """
        Returns a string containing the html for the graphiql webpage. It also caches the
        result using lru cache. This saves loading from disk each time it is invoked.
        Returns:
            The GraphiQL html page as a string
        """
        return get_graphiql_html(subscription_enabled=False)

    @staticmethod
    def should_render_graphiql(graphiql: bool, request: Request) -> bool:
        """
        Do the headers indicate that the invoker has requested html?
        Args:
            headers: A dictionary containing the headers in the request

        Returns:
            Whether html has been requested True for yes, False for no
        """
        if not graphiql:
            return False

        return any(
            supported_header in request.headers.get("accept", "")
            for supported_header in {"text/html", "*/*"}
        )

    @staticmethod
    def error_response(
        message: str,
        error_code: str,
        http_status_code: int,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        A wrapper for error responses
        Returns:
        An errors response
        """
        body = {"Code": error_code, "Message": message}

        return Response(body=body, status_code=http_status_code, headers=headers)

    def process_result(
        self, request: Request, result: ExecutionResult
    ) -> GraphQLHTTPResponse:
        return process_result(result)

    def execute_request(self, request: Request) -> Response:
        """
        Parse the request process it with strawberry and return a response
        Args:
            request: The chalice request this contains the headers and body

        Returns:
            A chalice response
        """

        if request.method not in {"POST", "GET"}:
            return self.error_response(
                error_code="MethodNotAllowedError",
                message="Unsupported method, must be of request type POST or GET",
                http_status_code=405,
            )
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = request.json_body
                if not (isinstance(data, dict)):
                    return self.error_response(
                        error_code="BadRequestError",
                        message=(
                            "Provide a valid graphql query "
                            "in the body of your request"
                        ),
                        http_status_code=400,
                    )
            except BadRequestError:
                return self.error_response(
                    error_code="BadRequestError",
                    message="Provide a valid graphql query in the body of your request",
                    http_status_code=400,
                )
        elif request.method == "GET" and request.query_params:
            data = parse_query_params(request.query_params)  # type: ignore

        elif request.method == "GET" and self.should_render_graphiql(
            self.graphiql, request
        ):
            return Response(
                body=self.render_graphiql(),
                headers={"content-type": "text/html"},
                status_code=200,
            )

        else:
            return self.error_response(
                error_code="UnsupportedMediaType",
                message="Unsupported Media Type",
                http_status_code=415,
            )

        try:
            request_data = parse_request_data(data)
        except MissingQueryError:
            return self.error_response(
                error_code="BadRequestError",
                message="No GraphQL query found in the request",
                http_status_code=400,
            )

        result: ExecutionResult = self._schema.execute_sync(
            request_data.query,
            variable_values=request_data.variables,
            context_value=request,
            operation_name=request_data.operation_name,
            root_value=None,
        )

        http_result = self.process_result(request, result)

        body = self.json_encoder(**self.json_dumps_params).encode(http_result)

        return Response(body=body)
