from aiohttp import web
from pepe_stream_server.routes import add_routes_to_app
from pepe_stream_server.routes.middlewares import authentication
from . import (
    startup_application,
    teardown_application,
)
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

app = web.Application(middlewares=[authentication])
add_routes_to_app(app)
app.on_startup.append(startup_application)
app.on_shutdown.append(teardown_application)

web.run_app(app)