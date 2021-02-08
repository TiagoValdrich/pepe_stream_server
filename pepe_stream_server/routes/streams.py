from aiohttp import web
from pepe_stream_server.models import Database, Stream
import logging
import os

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

routes.static("/live", os.getcwd() + "/live")


@routes.get("/streams")
async def get_all_streams(request: web.Request):
    db: Database = request.app["database"]
    streams = await Stream.get_all_streams(db.conn, raw_dict=True)

    return web.json_response(streams, status=200)


@routes.post("/stream")
async def create_stream(request: web.Request):
    if not request.body_exists:
        raise web.HTTPBadRequest(text="Invalid body!")

    db: Database = request.app["database"]
    body = await request.json()

    if "stream_name" not in body:
        raise web.HTTPBadRequest(text="Couldn't find stream_name in body!")

    if "rtsp_address" not in body:
        raise web.HTTPBadRequest(text="Couldn't find rtsp_address in body!")

    stream = Stream(
        body["stream_name"],
        body["rtsp_address"],
    )

    try:
        await stream.create(db.conn)
    except BaseException as e:
        logger.error(e)
        raise web.HTTPInternalServerError()

    return web.Response(status=200)


@routes.delete("/stream/{stream_name}")
async def create_stream(request: web.Request):
    db: Database = request.app["database"]
    stream_name = request.match_info["stream_name"]

    try:
        await Stream.delete_stream(db.conn, stream_name)
    except BaseException as e:
        logger.error(e)
        raise web.HTTPInternalServerError()

    return web.Response(status=200)


@routes.post("/stream/{stream_name}/connect")
async def connect_stream(request: web.Request):
    db: Database = request.app["database"]
    stream_name = request.match_info["stream_name"]

    try:
        stream: Stream = await Stream.find_stream_by_name(db.conn, stream_name)

        if not stream:
            raise web.HTTPNotFound(text="Couldn't find stream!")

        await stream.connect(db.conn)

    except BaseException as e:
        logger.error(e)
        raise web.HTTPInternalServerError()

    return web.Response(status=200)


@routes.post("/stream/{stream_name}/disconnect")
async def disconnect_stream(request: web.Request):
    db: Database = request.app["database"]
    stream_name = request.match_info["stream_name"]

    try:
        stream: Stream = await Stream.find_stream_by_name(db.conn, stream_name)

        if not stream:
            raise web.HTTPNotFound(text="Couldn't find stream!")

        await stream.disconnect(db.conn)

    except BaseException as e:
        logger.error(e)
        raise web.HTTPInternalServerError()

    return web.Response(status=200)