from django.http import HttpResponse, JsonResponse

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400


def success_response(data=None, status=HTTP_200_OK) -> HttpResponse:
    """
    >>> isinstance(success_response(), JsonResponse)
    True
    >>> success_response({"fib": [1, 1, 2, 3]}).content
    b'{"fib": [1, 1, 2, 3]}'
    >>> success_response().status_code
    200
    >>> success_response(status=201).status_code
    201
    """
    return JsonResponse(data=data, status=status, safe=False)


def error_response(message: str = None, status=HTTP_400_BAD_REQUEST) -> HttpResponse:
    """
    >>> isinstance(error_response(), JsonResponse)
    True
    >>> error_response("something bad happened").content
    b'{"message": "something bad happened"}'
    >>> error_response().status_code
    400
    >>> error_response(status=418).status_code
    418
    """
    error_data = {"message": message}
    return JsonResponse(data=error_data, status=status)
