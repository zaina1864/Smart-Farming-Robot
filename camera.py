# Web Streaming with PiCamera
# Source: http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
# Description: Streams MJPEG video from a Raspberry Pi camera to a web browser.

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

# HTML page to serve on the root
PAGE = """\
<html>
<head>
    <title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
    <center><h1>Raspberry Pi - Surveillance Camera</h1></center>
    <center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    """
    This class captures and buffers the latest video frame.
    It uses a condition variable to notify waiting clients when a new frame is available.
    """
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        # New JPEG frame starts with 0xFFD8
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                # Set current frame and notify clients
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    Handles incoming HTTP GET requests and serves the stream and HTML page.
    """
    def do_GET(self):
        if self.path == '/':
            # Redirect root to /index.html
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            # Serve the HTML page
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/stream.mjpg':
            # Serve MJPEG video stream
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            # Handle unknown routes
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """
    HTTP Server with thread support for handling multiple clients.
    """
    allow_reuse_address = True
    daemon_threads = True

# Main streaming logic
with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    
    # Uncomment this line if you need to rotate the camera view (e.g., upside down)
    # camera.rotation = 180
    
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)  # Serve on port 8000
        server = StreamingServer(address, StreamingHandler)
        print("Streaming started. Open http://<Pi-IP>:8000 in your browser.")
        server.serve_forever()
    finally:
        camera.stop_recording()
