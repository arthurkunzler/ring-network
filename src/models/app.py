from datetime import datetime
import socket
import threading
import time
import zlib
import random

from models.package import Package
from models.token_manager import TokenManager
import models.constants as Constants


class App:
    def __init__(self, dest_ip: str, dest_port: int, src_port: int, hostname: str, is_token_manager: bool = False, sleep_time: int = 0, token_manager: TokenManager = None):
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
        self.sleep_time = sleep_time
        self.token_rcvd_time = None
        self.token_manager = token_manager
        self.last_message_sent: Package = None
        self.already_resent = False

        # Vai gerar pela primeira vez
        if is_token_manager:
            self.token = self.token_manager.generate_token()
            self.token_rcvd_time = datetime.now()

        self.connect_socket()

    # Inicia as threads que irão receber as mensagens e verificar tokens
    def start(self):
        # Inicia thread para receber pacotes de outras maquinas
        self.thread_receiver = threading.Thread(
            target=self._start_receive, args=(), daemon=True)
        self.thread_receiver.start()

        self.thread_token_sleep = threading.Thread(
            target=self._start_tokensleep_check, args=(), daemon=True)
        self.thread_token_sleep.start()
        time.sleep(1)

    def connect_socket(self):
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.src_port))

    # Pega a primeira mensagem da fila
    def pop_first_message(self):
        message = self.messages_queue.pop(0) if (
            len(self.messages_queue) > 0) else None
        return message

    # Adiciona mensagem na fila com uma certa probabilidade de inserir crc com erro
    def add_message(self, dest_name: str, message: str):
        prob = random.random()
        crc = App._generate_crc(message)

        if prob < Constants.PROB_ERROR_INSERTION:  # Probabilidade de adicionar erro
            print(Constants.INSERTING_ERROR)
            # Adiciona em proporção ao crc para errar de propósito
            crc += int(prob*100)

        data = f"7777:{Constants.ErrorControl.NAOEXISTE.value};{self.hostname};{dest_name};{str(crc)};{message}"
        pkg = Package(data=data)
        print(f'pkg:\n {pkg}')
        self._insert_message(pkg)

    # Insere mensagem no fim da fila
    def _insert_message(self, message: Package):
        if len(self.messages_queue) < 10:
            self.messages_queue.append(message)
            return True
        else:
            print('Lista de mensagens está cheia!')
            return False

    # Gera o token se for gerenciador
    def generate_token(self):
        if self.is_token_manager:
            self.token_manager.generate_token()
            print(Constants.TOKEN_GENERATED)
        else:
            print(Constants.NOT_MANAGER)

    def _has_message(self):
        return len(self.messages_queue) > 0

    # Verifica se houve timeout no recebimento de token (se for gerenciador)
    def check_token_timeout(self):
        if (self.is_token_manager and (not self.token_manager.check_timeout())):
            # Token deu timeout, deve-se gerar um novo
            self.token = self.token_manager.generate_token()

    def remove_token(self):
        print(Constants.TOKEN_REMOVED)
        self.token = None

    # Envia token ao próximo host
    def send_token(self):
        if (self.token is not None and (not self.waiting_receive)):
            token_pkg = Package(data="9000")
            self.send_package(package=token_pkg)
            self.token = None
            self.token_rcvd_time = None
            if self.is_token_manager:
                self.token_manager.token = None

    # Envia pacote (vindo da fila ou de outro host) para o próximo host
    def send_package(self, package: Package):
        if self.closed:
            return
        if package.type == Constants.Prefix.DATA:
            pck = "7777:{0};{1};{2};{3};{4}".format(
                package.error_control.value, package.origin_name, package.dest_name, package.crc, package.text)
        elif package.type == Constants.Prefix.TOKEN:
            pck = "9000"
        package = pck.encode("utf-8")
        self.socket.sendto(package, (str(self.dest_ip), int(self.dest_port)))
        print(f'Package sent: {pck}')

    # Fecha conexão
    def close_socket(self):
        self.closed = True
        return self.socket.close()

    # Converte uma mensagem do socket para uma instância do tipo Package para facilitar o tratamento
    def _open_package(self, package: tuple) -> Package:
        pck = Package(data=package[0].decode("utf-8"))
        return pck

    # Verifica se o crc está correto
    def _verify_message_consistency(self, package: Package):
        return App._check_crc(pck=package)

    # Processa token recebido
    def _handle_receive_token(self, package):
        self.token = package.text
        self.token_rcvd_time = datetime.now()
        if self.is_token_manager:
            if not self.token_manager.handle_token(self.token):
                self.token = None
            else:
                print(Constants.TOKEN_RECEIVED)

        self.send_message()

    # Envia/reenvia mensagem da fila
    def send_message(self):
        if self.token is not None:
            if self.last_message_sent is None:
                if (len(self.messages_queue) > 0):
                    msg = self.messages_queue.pop(0)
                    self.send_package(msg)
                    # Setta flag indicando que enviamos mensagem e que estamos esperando ela retornar
                    self.waiting_receive = True
                    self.last_message_sent = msg
                else:
                    print('No messages to send. Waiting token sleep..')

            else:
                print(Constants.RESENDING_MESSAGE)
                self.send_package(self.last_message_sent)
                self.last_message_sent = None
                self.waiting_receive = False

    def app_status(self):
        return f'Hostname: {self.hostname}, Next host: {self.dest_ip}:{self.dest_port}, Messages in queue: {len(self.messages_queue)}, Waiting to receive sent message: {self.waiting_receive}, Has Token: {bool(self.token)}'

    # Processa mensagem recebida
    def _handle_receive_data(self, package: Package):
        # Se destino sou eu, verifica consistência
        if package.dest_name == self.hostname:
            if self._verify_message_consistency(package):
                package.error_control = Constants.ErrorControl.ACK
                print(package.cool_message())
            else:
                package.error_control = Constants.ErrorControl.NACK
                print(Constants.ERROR_IN_MESSAGE)
        elif package.dest_name == Constants.BROADCAST_MESSAGE and package.origin_name != self.hostname:
            print(package.cool_message())

        # Se não fui eu quem mandou, repassa mensagem para o próximo host
        if package.origin_name != self.hostname:
            self.send_package(package=package)

        # # Se fui eu quem mandou, houve falha e já houve reenvio
        elif self.already_resent and (package.origin_name == self.hostname and package.error_control == Constants.ErrorControl.NACK):
            self.already_resent = False
            self.waiting_receive = False
            self.last_message_sent = None

        # Se fui eu quem mandou, houve falha mas ainda não houve reenvio
        elif package.origin_name == self.hostname and package.error_control == Constants.ErrorControl.NACK:
            print(Constants.RESENDING_MESSAGE)
            self._insert_message(message=self.last_message_sent)
            self.already_resent = True
            self.waiting_receive = False
            self.last_message_sent = None

        # Se fui eu quem mandou e não houve falha
        else:
            self.waiting_receive = False
            self.last_message_sent = None

    # Começa a ouvir mensagens na porta definida
    def _start_receive(self):
        port = self.socket.getsockname()[1]
        print(f"Client is receiving messages on port {port}")
        while True:
            # Se receber mensagem, processa a mesma
            pck = self._open_package(self.socket.recvfrom(1024))
            if pck.type == Constants.Prefix.TOKEN:
                self._handle_receive_token(pck)
            elif pck.type == Constants.Prefix.DATA:
                self._handle_receive_data(pck)
            else:
                print(Constants.INVALID_PACKAGE)

            print(f"Nova mensagem recebida: {pck}")

    # Começa a verificar situação do token
    def _start_tokensleep_check(self):
        print(f"Thread is checking for token sleep")
        while True:
            time.sleep(0.001)
            if self.token_rcvd_time and self._check_if_token_expired():
                print("Token sleep time expired, sending to next..")
                self.send_token()

    # Veririca se token expirou
    def _check_if_token_expired(self) -> bool:
        if self.token_rcvd_time:
            time_since_received = int(
                (datetime.now()-self.token_rcvd_time).total_seconds())  # em segundos
            return time_since_received >= self.sleep_time
        return False

    # Verifica crc
    @staticmethod
    def _check_crc(pck: Package) -> bool:
        b_text = pck.text.encode("utf-8")
        crc = zlib.crc32(b_text)
        return crc == pck.crc

    # Gera crc
    @staticmethod
    def _generate_crc(text: str) -> int:
        ecd = text.encode("utf-8")
        return zlib.crc32(ecd)
