import socket
import threading
import time

from models.package import Package
from models.message import Message
from models.token_manager import TokenManager


class App:
    def __init__(self, dest_ip: str, dest_port: int, src_port: int, hostname: str, is_token_manager: bool = False, timeout_token: int = 0, minimum_time: int = 0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.dest_ip = dest_ip
        self.hostname = hostname
        self.dest_port = dest_port
        self.src_port = src_port
        self.token = None

        self.closed = False
        self.messages_queue = list()
        self.is_token_manager = is_token_manager
        self.token_manager = TokenManager(
            minimum_time=minimum_time, timeout=timeout_token)

        if is_token_manager:
            self.token_manager.generate_token()

        self.connect_socket()

    def start(self):
        self.thread_receiver = threading.Thread(
            target=self._start_receive, args=(), daemon=True)
        self.thread_receiver.start()
        time.sleep(1)

    def connect_socket(self):
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.src_port))

    def get_first_message(self):
        message = self.messages_queue.pop(0) if (
            len(self.messages_queue) > 0) else None
        return message

    def insert_message(self, message: Message):
        if len(self.messages_queue) < 10:
            # TODO
            # Fazer tratamento de mensagem antes de inserir?
            self.messages_queue.append(message)
            return True
        else:
            print('Lista de mensagens está cheia!')
            return False

    def _has_message(self):
        return len(self.messages_queue) > 0

    def check_token_timeout(self):
        if (self.is_token_manager and not self.token_manager.check_timeout()):
            # Token deu timeout, deve-se gerar um novo
            self.token = self.token_manager.generate_token()

    def remove_token(self):
        self.token = None

    def send_token(self):
        # TODO
        # Implementar lógica de enviar token para a próxima máquina
        if self.token is not None:
            pass

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

    def _verify_message_consistency(self, package):
        consistent = True
        return consistent

    def _handle_receive_token(self, package):
        self.my_turn = True
        self.token = package.text
        if self.is_token_manager:
            if not self.token_manager.handle_token():
                # TODO tratar situações de problema com token
                pass

    def _handle_receive_data(self, package):
        # Se for consistente, trata a mensagem
        if self._verify_message_consistency(package):
            pass
        # Caso contrário, marca como NACK
        else:
            pass

    def _start_receive(self):
        port = self.socket.getsockname()[1]
        while True:
            print(f"Client is receiving messages on port {port}")
            pck = self._open_package(self.socket.recvfrom(1024))
            if pck.type == "9000":
                self._handle_receive_token(pck)
                # TODO ver se precisa de algo a mais p tratar se pacote for Token
            elif pck.type == "7777":
                self._handle_receive_data(pck)
                # TODO tratar pacote se for de dados

            print(f"Nova mensagem: {pck}")
