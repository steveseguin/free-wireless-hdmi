"""Offline checks for the documented Python 3 capture entry point.

Run with: python3 -m unittest discover -s tests -v
Camera sockets, the keepalive thread and the image viewer are inert fixtures.
JPEG decoding and NumPy conversion use the real installed dependencies.
"""

import ast
import errno
from io import BytesIO
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image


SOURCE = Path(__file__).resolve().parents[1] / "windowcap.py"


class StopCapture(BaseException):
    """Stop the script's infinite loops without being caught as a camera error."""


class CameraSocket:
    def __init__(self):
        self.connections = []
        self.requests = []
        self.receives = []

    def connect(self, target):
        if self.requests:
            raise StopCapture()
        if self.connections:
            raise OSError(errno.EISCONN, "already connected")
        self.connections.append(target)

    def sendall(self, data):
        # Like a real Python 3 socket, reject text before examining the connection.
        memoryview(data)
        if not self.connections:
            raise OSError(errno.ENOTCONN, "not connected")
        if len(self.requests) == 2:
            # End after two successful refreshes via the reconnect handler.
            raise OSError("test capture complete")
        self.requests.append(data)

    def sendto(self, data, target):
        # Retained so the identical tests can reproduce the unmodified script.
        return self.sendall(data)

    def recv(self, size):
        self.receives.append(size)
        return b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"


class CaptureSocket:
    def __init__(self, packets):
        self.packets = iter(packets)
        self.bindings = []

    def bind(self, address):
        self.bindings.append(address)

    def recvfrom(self, size):
        try:
            return next(self.packets), ("192.0.2.20", 5555)
        except StopIteration:
            raise StopCapture()


def load_script(packets=(), local_ip=None, camera_ip=None):
    tree = ast.parse(SOURCE.read_bytes(), filename=str(SOURCE))
    # Simulate the README's instruction to edit these two settings. All other
    # source, including imports and the entire top-level capture loop, is intact.
    overrides = {"MY_IP": local_ip, "THEIR_IP": camera_ip}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            value = overrides.get(node.targets[0].id)
            if value is not None:
                node.value = ast.copy_location(ast.Constant(value), node.value)
    camera = CameraSocket()
    capture = CaptureSocket(packets)
    shown = []
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    with patch("socket.socket", side_effect=[capture, camera]), \
            patch("threading.Thread"), \
            patch.object(Image.Image, "show", lambda image: shown.append(np.array(image))):
        try:
            exec(compile(tree, str(SOURCE), "exec"), namespace)
        except StopCapture:
            pass
    return namespace, camera, capture, shown


def jpeg_packet(color):
    data = BytesIO()
    Image.new("RGB", (8, 6), color).save(data, format="JPEG")
    return b"camera-header" + data.getvalue() + b"camera-trailer"


class WindowCaptureTests(unittest.TestCase):
    def test_displays_two_received_jpegs_with_real_pillow(self):
        _, _, capture, shown = load_script([
            jpeg_packet((240, 0, 0)), jpeg_packet((0, 240, 0)),
        ])
        self.assertEqual(capture.bindings, [("192.168.1.166", 5555)])
        self.assertEqual(len(shown), 2)
        self.assertEqual(shown[0].shape, (6, 8, 3))
        self.assertGreater(shown[0][0, 0, 0], 230)
        self.assertGreater(shown[1][0, 0, 1], 230)

    def test_bytes_decoder_returns_numpy_pixels(self):
        namespace, _, _, _ = load_script()
        data = BytesIO()
        Image.new("RGB", (3, 2), (10, 20, 30)).save(data, format="PNG")
        pixels = namespace["bytes_to_ndarray"](data.getvalue())
        np.testing.assert_array_equal(pixels, np.full((2, 3, 3), (10, 20, 30)))

    def test_keepalive_sends_bytes_to_the_configured_camera(self):
        for local_ip, camera_ip in [
            ("192.168.1.166", "192.168.1.222"),
            ("192.0.2.10", "192.0.2.20"),
        ]:
            with self.subTest(camera_ip=camera_ip):
                namespace, camera, capture, _ = load_script(
                    local_ip=local_ip, camera_ip=camera_ip,
                )
                with patch("time.sleep") as sleep:
                    with self.assertRaises(StopCapture):
                        namespace["keepalive"](local_ip, camera_ip)
                self.assertEqual(capture.bindings, [(local_ip, 5555)])
                self.assertEqual(camera.connections, [(camera_ip, 80)])
                self.assertEqual(len(camera.requests), 2)
                self.assertEqual(camera.requests[0], camera.requests[1])
                request = camera.requests[0]
                self.assertIsInstance(request, bytes)
                self.assertIn(b"GET /cam.cgi?mode=startstream&value=5555 HTTP/1.1", request)
                self.assertIn(("Host: " + camera_ip).encode("ascii"), request)
                self.assertTrue(request.endswith(b"\r\n\r\n"))
                self.assertEqual(request.count(b"\r\n\r\n"), 1)
                self.assertEqual(camera.receives, [1024, 1024])
                self.assertEqual(sleep.call_count, 2)
                sleep.assert_called_with(8)

    def test_socket_fixture_matches_python3_text_rejection(self):
        # No connection is made: real sockets reject str before sending anything.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as real:
            with self.assertRaises(TypeError):
                real.sendto("GET / HTTP/1.1\r\n\r\n", ("127.0.0.1", 1))
        with self.assertRaises(TypeError):
            CameraSocket().sendto("GET / HTTP/1.1\r\n\r\n", ("127.0.0.1", 1))


if __name__ == "__main__":
    unittest.main()
