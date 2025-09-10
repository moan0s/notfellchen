
def headers(headers):
    """Decorator adding arbitrary HTTP headers to the response.

    This decorator adds HTTP headers specified in the argument (map), to the
    HTTPResponse returned by the function being decorated.

    Example:

    @headers({'Refresh': '10', 'X-Bender': 'Bite my shiny, metal ass!'})
    def index(request):
        ....
    Source: https://djangosnippets.org/snippets/275/
    """
    def headers_wrapper(fun):
        def wrapped_function(*args, **kwargs):
            response = fun(*args, **kwargs)
            for key in headers:
                response[key] = headers[key]
            return response
        return wrapped_function
    return headers_wrapper

