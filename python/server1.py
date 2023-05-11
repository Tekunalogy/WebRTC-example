import os
from aiohttp import web
from send_offer import *
from CORS import *

ROOT = os.path.dirname(__file__)

async def index(request):
    """ Index Method

    This method handles a `GET` request to the server's index route.
    It returns a `JSON` response with test data.

    Args:
        `request`: A `web.Request` object representing the request received by the server.

    Returns:
        A `web.Response` object containing a JSON payload with a test message.

    Raises:
        `None`
    """
    return web.Response(
        content_type="application/json", 
        text=json.dumps(
            {"mydata": "test"}
        )
    )

if __name__ == "__main__":
    """    
    This is the main method of the application.
    It initializes a web.Application object and adds the necessary routes for handling requests.
    It also sets up a CORS object for allowing cross-origin resource sharing for all routes.
    The method then runs the web application on localhost:8080
    """
    app = web.Application()
    
    cors = CORS_obj(app)
    
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)
    
    # Configure CORS for all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    web.run_app(app, host="127.0.0.1", port="8080")