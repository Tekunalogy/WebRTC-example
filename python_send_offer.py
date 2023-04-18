from opencv_track import *
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

# store unique peer connections
peer_connections = set()

async def offer(request):
    print(request)
    # Create a new RTCPeerConnection
    pc = RTCPeerConnection()
    url = 'ws://localhost:8080'
    channel = pc.createDataChannel('my_channel', {'reliable': True, 'ordered': True, 'protocol': 'json'})
    channel.url = url
    peer_connections.add(pc) # keeps track of all connections

    # Create an offer and set it as the local description
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    '''
    Return offer to the client
    SDP: Session Description Protocol
    Type: type of SDP message that is being exchanged.
        Two Types:
            - Offers: Sent by a peer to initiate a connection
            - Answers: Sent in response to an offer. Accept or reject connection
    '''
    return web.json_response({
        'sdp':  pc.localDescription.sdp,
        'type': pc.localDescription.type
    })
    
async def handle_answer(request):
    # Get the session description from the client
    params = await request.json()
    sdp = params['sdp']
    type = params['type']

    # Create a new RTCPeerConnection
    pc = RTCPeerConnection()

    # Set the remote description from the client's answer
    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=type))

    # Return a success response
    return web.json_response({'result': 'success'})

async def stream(request):
    # Create a new RTCPeerConnection
    pc = RTCPeerConnection()
    camera = None
    
    try:
        # setup opencv camera capture
        camera = cv2.VideoCapture(0)
        
        # Add a video track to the RTCPeerConnection
        video_track = OpenCVVideoTrack(camera)
        pc.addTrack(video_track)

        # Create an offer and set it as the local description
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Return the offer to the client
        return web.json_response({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })

    finally:
        # Close the RTCPeerConnection and the video capture device
        await pc.close()
        if camera is not None:
            camera.release()
            
async def on_shutdown(app):
    # Close all peer connections and release all video capture devices
    for pc in peer_connections:
        await pc.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    # Create an aiohttp web Application and register the routes
    app = web.Application()
    app.router.add_get('/offer', offer)
    app.router.add_post('/answer', handle_answer)
    app.router.add_get('/stream', stream)

    # Register a callback for when the application shuts down
    app.on_shutdown.append(on_shutdown)

    # Start the application
    web.run_app(app, host='localhost', port=8081)