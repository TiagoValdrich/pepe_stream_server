import json

from aiohttp.web import Request, Response, RouteTableDef
from pepe_stream_server.models import Database, Stream

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

routes = RouteTableDef()


@routes.post("/offer")
async def offer(request: Request):
    db: Database = request.app["database"]
    webrtc_connections: set = request.app["webrtc_connections"]
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    webrtc_connections.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            webrtc_connections.discard(pc)

    stream = await Stream.find_stream_by_name(
        db.conn, params["streamInfo"]["streamName"]
    )

    player = MediaPlayer(stream.rtsp_address)

    await pc.setRemoteDescription(offer)

    for t in pc.getTransceivers():
        if t.kind == "audio" and player.audio:
            pc.addTrack(player.audio)
        elif t.kind == "video" and player.video:
            pc.addTrack(player.video)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )