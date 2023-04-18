import cv2
from av import VideoFrame
from aiortc.contrib.media import MediaStreamTrack

MJPG = cv2.VideoWriter_fourcc(*'MJPG')

class OpenCVVideoTrack(MediaStreamTrack):
    def __init__(self, capture: cv2.VideoCapture):
        super().__init__()  # don't forget this!
        self.capture = capture
        self.capture.set(cv2.CAP_PROP_FOURCC, MJPG)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # manual mode
        self.capture.set(cv2.CAP_PROP_EXPOSURE, 50)

    async def recv(self):
        # Capture a frame from OpenCV
        ret, frame = self.capture.read()
        if not ret:
            return None

        # Convert the frame to RTP video format
        frame = VideoFrame.from_ndarray(frame, format='bgr24')
        frame.pts = int(self.timestamp * 90)  # convert time to 90kHz clock
        return frame