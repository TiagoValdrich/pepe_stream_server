import logging
import asyncio

from aiohttp.web import Application
from pepe_stream_server.models import Database, Stream

logger = logging.getLogger(__name__)


async def startup_application(app: Application) -> None:
    db = Database()
    db.create_conn()

    app["database"] = db
    app["webrtc_connections"] = set()

    try:
        streams = await Stream.get_startup_streams(db.conn, raw_dict=False)

        for stream in streams:
            await stream.connect(db.conn)
    except Exception as e:
        logger.exception("An error has occured on startup streams", e)


async def teardown_application(app: Application) -> None:
    db: Database = app["database"]
    webrtc_connections = app["webrtc_connections"]

    try:
        coros = [pc.close() for pc in webrtc_connections]
        await asyncio.gather(*coros)
        webrtc_connections.clear()

        streams = await Stream.get_all_streams(db.conn, raw_dict=False)

        for stream in streams:
            await stream.disconnect(db.conn)
    except Exception as e:
        logger.exception("An error has occurred when disconnecting streams", e)
    finally:
        if db.initialized:
            db.close()