from aiohttp import web
from pepe_stream_server.routes import add_routes_to_app
from pepe_stream_server.routes.middlewares import authentication
from . import (
    startup_application,
    teardown_application,
)
from dotenv import load_dotenv

import logging
import ssl
import os

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

ssl_context = None

if os.environ.get("SSL_CERT_FILE_PATH") and os.environ.get("SSL_KEY_FILE_PATH"):
    ssl_context = ssl.SSLContext()
    ssl_context.load_cert_chain(
        os.environ.get("SSL_CERT_FILE_PATH"), os.environ.get("SSL_KEY_FILE_PATH")
    )

app = web.Application(middlewares=[authentication])
add_routes_to_app(app)
app.on_startup.append(startup_application)
app.on_shutdown.append(teardown_application)

web.run_app(app, host="0.0.0.0", port=8080, ssl_context=ssl_context)