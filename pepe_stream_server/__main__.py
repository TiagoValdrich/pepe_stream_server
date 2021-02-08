from aiohttp import web
from pepe_stream_server.routes import add_routes_to_app
from . import start_database, close_database_connection
import logging

logging.basicConfig(level=logging.DEBUG)

app = web.Application()
add_routes_to_app(app)
app.on_startup.append(start_database)
app.on_shutdown.append(close_database_connection)

web.run_app(app)