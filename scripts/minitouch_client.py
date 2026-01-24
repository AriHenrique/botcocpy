import socket
import time

class MiniTouch:
    def __init__(self, host="127.0.0.1", port=1111, width=1600, height=900):
        self.width = width
        self.height = height
        self.max_x = 32767
        self.max_y = 32767

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self._handshake()

    def _handshake(self):
        for _ in range(3):
            print(self.sock.recv(1024).decode(errors="ignore").strip())

    # ===== Utils =====
    def _scale(self, x, y):
        sx = int(x / self.width * self.max_x)
        sy = int(y / self.height * self.max_y)
        return sx, sy

    def send(self, cmd):
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.sock.sendall(cmd.encode())
        time.sleep(0.005)

    # ===== Low level =====
    def down(self, contact, x, y, pressure=50):
        sx, sy = self._scale(x, y)
        self.send(f"d {contact} {sx} {sy} {pressure}")

    def move(self, contact, x, y, pressure=50):
        sx, sy = self._scale(x, y)
        self.send(f"m {contact} {sx} {sy} {pressure}")

    def up(self, contact):
        self.send(f"u {contact}")

    def commit(self):
        self.send("c")

    def wait(self, ms):
        self.send(f"w {ms}")

    # ===== High level =====
    def tap(self, x, y):
        self.down(0, x, y)
        self.commit()
        self.wait(30)
        self.up(0)
        self.commit()

    def pinch_zoom_out(self, x1, y1, x2, y2, steps=20, delay=15):
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        self.down(0, x1, y1)
        self.down(1, x2, y2)
        self.commit()
        self.wait(50)

        for i in range(1, steps + 1):
            nx1 = int(x1 + (cx - x1) * i / steps)
            ny1 = int(y1 + (cy - y1) * i / steps)

            nx2 = int(x2 + (cx - x2) * i / steps)
            ny2 = int(y2 + (cy - y2) * i / steps)

            self.move(0, nx1, ny1)
            self.move(1, nx2, ny2)
            self.commit()
            self.wait(delay)

        self.up(0)
        self.up(1)
        self.commit()

    def close(self):
        self.sock.close()
