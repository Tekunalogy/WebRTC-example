import json
import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from usb_camera_track import *

# unique peer connections
peer_connections = set()

async def offer(request):
    """ Offer Method (WebRTC Offer)

    Overview:
        This method handles a `POST` request to create a WebRTC offer.
        It expects a `JSON` payload with an "sdp", "type", and "device_id" field.
        The method initializes an `RTCPeerConnection` object with the media source.
        Returns a response containing the local description.

    Args:
        `request`: A `web.Request` object representing the request received by the server.

    Returns:
        A `web.Response` object containing a `JSON` payload with the local description.

    Raises:
        `None`
    """
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    print(params["sdp"])

    pc = RTCPeerConnection()
    peer_connections.add(pc)
    print(len(peer_connections))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            peer_connections.discard(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()
            peer_connections.discard(pc)
    
    # open media source
    video = create_usb_camera_track(device_id=params["device_id"])
    pc.addTrack(video)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )

async def on_shutdown(app):
    """ On-Shutdown Method

        Overview:
            This method handles the shutdown of the server by closing all peer connections.

        Args:
            app: A web.Application object representing the server.

        Returns:
            None

        Raises:
            None
    """
    # close peer connections
    try:
        coros = [pc.close() for pc in peer_connections]
        await asyncio.gather(*coros)
        peer_connections.clear()
    except:
        print("Shut down the server.")