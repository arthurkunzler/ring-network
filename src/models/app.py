import socket
import threading
import time

from src.models.package import Package

class App:
    def __init__(self, dest_ip: str, dest_port: int, src_port: int, hostname: str, sleeptime: int, start_w_token: bool):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.dest_ip = dest_ip
        self.hostname = hostname
        self.sleeptime = sleeptime
        self.dest_port = dest_port
        self.src_port = src_port

        self.my_turn = start_w_token
        self.closed = False
        self.messages_queue = list()

        self.connect_socket()

    def start(self):
        self.thread_receiver = threading.Thread(
            target=self._start_receive, args=(), daemon=True)
        self.thread_receiver.start()
        time.sleep(1)

    def connect_socket(self):
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.src_port))

    def send_package(self, data: str):
        if self.closed:
            return

        package = data.encode("utf-8")
        self.socket.sendto(package, (self.dest_ip, self.dest_port))

    def close_socket(self):
        self.closed = True
        return self.socket.close()

    def _open_package(self, package: tuple) -> Package:
        pck = Package(data=package[0].decode("utf-8"))
        return pck

    def _start_receive(self):
        port = self.socket.getsockname()[1]
        while True:
            print(f"Client is receiving messages on port {port}")
            pck = self._open_package(self.socket.recvfrom(1024))
            if pck.type == "9000":
                self.my_turn = True
                # TODO ver se precisa de algo a mais p tratar se pacote for Token
            elif pck.type == "7777":
                # TODO tratar pacote se for de dados
                pass

            print(f"Nova mensagem: {pck}")
