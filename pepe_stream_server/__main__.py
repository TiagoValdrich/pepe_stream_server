from aiohttp import web
from pepe_stream_server.routes import add_routes_to_app
from . import (
    startup_application,
    teardown_application,
)
import logging

logging.basicConfig(level=logging.DEBUG)

app = web.Application()
add_routes_to_app(app)
app.on_startup.append(startup_application)
app.on_shutdown.append(teardown_application)

web.run_app(app)