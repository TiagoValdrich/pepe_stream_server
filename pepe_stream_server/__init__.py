from aiohttp.web import Application
from pepe_stream_server.models.database import Database


async def start_database(app: Application):
    db = Database()
    db.create_conn()

    app["database"] = db


async def close_database_connection(app: Application):
    if app["database"].initialized:
        app["database"].close()