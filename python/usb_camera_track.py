import platform
from aiortc.contrib.media import MediaPlayer, MediaRelay

usb_cams = {}
relay = None

def create_usb_camera_track(resolution="1920x1080", framerate=30, device_id="/dev/video2"):
    """ Create USB Camera Track Method

    This method creates a video track from a USB camera. It takes in optional parameters
    for `resolution`, `framerate`, and `device_id`. The method first initializes the options for
    the video stream, and creates a `MediaRelay` object if it does not already exist. It then
    checks if a `MediaPlayer` object is already created for the given device ID. If not, it
    initializes a new `MediaPlayer` object. Finally, the method returns the video track.

    Args:
        `resolution`: A string representing the resolution of the video stream. Defaults to `1920x1080`.
        
        `framerate`: An integer representing the framerate of the video stream. Defaults to `30`.
        
        `device_id`: A string representing the device ID of the USB camera. Defaults to `/dev/video2`.

    Returns:
        `MediaStreamTrack` of specified USB camera.

    Raises:
        `None`
    """
    global relay, usb_cam
    
    print(device_id)

    options = {"framerate": str(framerate), "video_size": resolution}
    if relay is None:
        relay = MediaRelay()
        
    if usb_cams.get(device_id) is None:
        if platform.system() == "Darwin":
            usb_cams[device_id] = MediaPlayer(
                "default:none", format="avfoundation", options=options
            )
        elif platform.system() == "Windows":
            usb_cams[device_id] = MediaPlayer(
                "video=Integrated Camera", format="dshow", options=options
            )
        else:
            usb_cams[device_id] = MediaPlayer(device_id, format="v4l2", options=options)
        
    return relay.subscribe(usb_cams[device_id].video)
