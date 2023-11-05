import socket
import threading
import time
import zlib

from models.package import Package
from models.message import Message
from models.token_manager import TokenManager
from src.models.constants import INVALID_PACKAGE, ErrorControl, Prefix


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
        while not self.closed:
            if self.token and len(self.messages_queue) > 0:
                self.send_package(package=self.pop_first_message())

    def connect_socket(self):
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.src_port))

    def pop_first_message(self):
        message = self.messages_queue.pop(0) if (
            len(self.messages_queue) > 0) else None
        return message

    def insert_message(self, message: Package):
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
            self.send_package(package=Package(data="9000"))

    def send_package(self, package: Package):
        if self.closed:
            return
        if package.type == Prefix.DATA:
            pck = "7777:{0};{1};{2};{3};{4}".format(package.error_control, package.origin_name, package.dest_name, package.crc, package.text)
        elif package.type == Prefix.TOKEN:
            pck = "9000"
        package = pck.encode("utf-8")
        self.socket.sendto(package, (self.dest_ip, self.dest_port))

    def close_socket(self):
        self.closed = True
        return self.socket.close()

    def _open_package(self, package: tuple) -> Package:
        pck = Package(data=package[0].decode("utf-8"))
        return pck

    def _verify_message_consistency(self, package: Package):
        # TODO o que precisa verificar aqui alem do CRC?
        return self._check_crc(pck=package)

    def _handle_receive_token(self, package):
        self.my_turn = True
        self.token = package.text
        if self.is_token_manager:
            if not self.token_manager.handle_token():
                # TODO tratar situações de problema com token
                pass

    def _handle_receive_data(self, package: Package):
        # Se destino for eu, verifica consistencia
        if package.dest_name == self.hostname:
            # TODO ver error_control?
            if not self._verify_message_consistency(package):
                package.error_control = ErrorControl.ACK
            else:
                package.error_control = ErrorControl.NACK
        else:
            package.error_control = ErrorControl.NAOEXISTE
        self.insert_message(message=package)

    def _start_receive(self):
        port = self.socket.getsockname()[1]
        while True:
            print(f"Client is receiving messages on port {port}")
            pck = self._open_package(self.socket.recvfrom(1024))
            if pck.type == Prefix.TOKEN:
                self._handle_receive_token(pck)
                # TODO ver se precisa de algo a mais p tratar se pacote for Token
            elif pck.type == Prefix.DATA:
                self._handle_receive_data(pck)
                # TODO tratar pacote se for de dados
            else:
                print(INVALID_PACKAGE)

            print(f"Nova mensagem recebida: {pck}")
    
    def _check_crc(self, pck: Package) -> bool:
        b_text = pck.text.encode("utf-8")
        crc = zlib.crc32(b_text)
        return crc == pck.crc