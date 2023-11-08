import socket
import threading
import time
import zlib
import random

from models.package import Package
from models.token_manager import TokenManager
import models.constants as Constants


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
        self.waiting_receive = False
        self.token_manager = TokenManager(
            minimum_time=minimum_time, timeout=timeout_token)
        self.last_message_sent = None

        if is_token_manager:
            self.token_manager.generate_token()

        self.connect_socket()

    def start(self):
        self.thread_receiver = threading.Thread(
            target=self._start_receive, args=(), daemon=True)
        self.thread_receiver.start()
        time.sleep(1)
        # TODO
        # while not self.closed:
        #     if self.token and len(self.messages_queue) > 0:
        #         self.send_package(package=self.pop_first_message())

    def connect_socket(self):
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.src_port))

    def pop_first_message(self):
        message = self.messages_queue.pop(0) if (
            len(self.messages_queue) > 0) else None
        return message

    def add_message(self, dest_name: str, message: str):
        prob = random.random()
        crc = App._generate_crc(message)

        if prob < 0.15:  # 15% de probabilidade de adicionar erro
            print(Constants.INSERTING_ERROR)
            crc += int(prob*100)

        data = f"7777:{Constants.ErrorControl.NAOEXISTE.value};{self.hostname};{dest_name};{str(crc)};{message}"
        pkg = Package(data=data)
        print(f'pkg:\n {pkg}')
        self._insert_message(pkg)

    def _insert_message(self, message: Package):
        if len(self.messages_queue) < 10:
            self.messages_queue.append(message)
            return True
        else:
            print('Lista de mensagens está cheia!')
            return False

    def generate_token(self):
        if self.is_token_manager:
            self.token_manager.generate_token()
            print(Constants.TOKEN_GENERATED)
        else:
            print(Constants.NOT_MANAGER)

    def _has_message(self):
        return len(self.messages_queue) > 0

    def check_token_timeout(self):
        if (self.is_token_manager and (not self.token_manager.check_timeout())):
            # Token deu timeout, deve-se gerar um novo
            self.token = self.token_manager.generate_token()

    def remove_token(self):
        print(Constants.TOKEN_REMOVED)
        self.token = None

    def send_token(self):
        if (self.token is not None and (not self.waiting_receive)):
            self.send_package(package=Package(data="9000"))
            self.token = None
            if self.is_token_manager:
                self.token_manager.token = None

    def send_package(self, package: Package):
        if self.closed:
            return
        if package.type == Constants.Prefix.DATA:
            pck = "7777:{0};{1};{2};{3};{4}".format(
                package.error_control, package.origin_name, package.dest_name, package.crc, package.text)
            self.last_message_sent = pck
        elif package.type == Constants.Prefix.TOKEN:
            pck = "9000"
        package = pck.encode("utf-8")
        self.socket.sendto(package, (self.dest_ip, self.dest_port))
        print(f'Package sent: {pck}')

    def close_socket(self):
        self.closed = True
        return self.socket.close()

    def _open_package(self, package: tuple) -> Package:
        pck = Package(data=package[0].decode("utf-8"))
        return pck

    def _verify_message_consistency(self, package: Package):
        return App._check_crc(pck=package)

    def _handle_receive_token(self, package):
        self.token = package.text
        if self.is_token_manager:
            if not self.token_manager.handle_token(self.token):
                # TODO tratar situações de problema com token
                pass

        self.send_message()

    def send_message(self):
        # TODO
        # Finalizar lógica de reenvio
        if self.last_message_sent is None:
            if (len(self.messages_queue) > 0):
                msg = self.messages_queue.pop(0)
                self.send_package(msg)
                # Setta flag indicando que enviamos mensagem e que estamos esperando ela retornar
                self.waiting_receive = True
            else:
                print('No messages to send')
        # Significa que deve fazer o reenvio
        else:
            self.send_package(self.last_message_sent)

    def app_status(self):
        return f'Hostname: {self.hostname}, Next host: {self.dest_ip}:{self.dest_port}, Messages in queue: {len(self.messages_queue)}, Waiting to receive sent message: {self.waiting_receive}'

    def _handle_receive_data(self, package: Package):
        # Se destino for eu, verifica consistencia
        if package.dest_name == self.hostname:
            if self._verify_message_consistency(package):
                package.error_control = Constants.ErrorControl.ACK
                print(package.cool_message())
            else:
                package.error_control = Constants.ErrorControl.NACK
        else:
            package.error_control = Constants.ErrorControl.NAOEXISTE
            if package.dest_name == Constants.BROADCAST_MESSAGE:
                print(package.cool_message())

        if package.origin_name != self.hostname:
            self.send_package(package=package)
        else:
            self.last_message_sent = None
            self.waiting_receive = False
            self.send_token()

    def _start_receive(self):
        port = self.socket.getsockname()[1]
        while True:
            print(f"Client is receiving messages on port {port}")
            pck = self._open_package(self.socket.recvfrom(1024))
            if pck.type == Constants.Prefix.TOKEN:
                self._handle_receive_token(pck)
            elif pck.type == Constants.Prefix.DATA:
                self._handle_receive_data(pck)
            else:
                print(Constants.INVALID_PACKAGE)

            print(f"Nova mensagem recebida: {pck}")

    @staticmethod
    def _check_crc(pck: Package) -> bool:
        b_text = pck.text.encode("utf-8")
        crc = zlib.crc32(b_text)
        return crc == pck.crc

    @staticmethod
    def _generate_crc(text: str) -> int:
        ecd = text.encode("utf-8")
        return zlib.crc32(ecd)
