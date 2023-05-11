import aiohttp_cors

def CORS_obj(app):
    """ CORS Object Method

    This method creates and returns a CORS object for the specified app.
    Allows for all origins, credentials, methods, and headers.

    Args:
        `app`: A `web.Application` object representing the server.

    Returns:
        `aiohttp_cors.CorsConfig` object

    Raises:
        `None`
    """
    # Create a CORS object
    return aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers="*",
        ),
    })