from aiohttp.web import Application
from pepe_stream_server.models import Database, Stream
import logging

logger = logging.getLogger(__name__)


async def startup_application(app: Application) -> None:
    db = Database()
    db.create_conn()

    app["database"] = db

    try:
        streams = await Stream.get_startup_streams(db.conn, raw_dict=False)

        for stream in streams:
            await stream.connect(db.conn)
    except Exception as e:
        logger.exception("An error has occured on startup streams", e)


async def teardown_application(app: Application) -> None:
    db: Database = app["database"]

    try:
        streams = await Stream.get_all_streams(db.conn, raw_dict=False)

        for stream in streams:
            await stream.disconnect(db.conn)
    except Exception as e:
        logger.exception("An error has occurred when disconnecting streams", e)
    finally:
        if db.initialized:
            db.close()