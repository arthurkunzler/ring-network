import socket
import threading
import time

class App:
    def __init__(self, dest_ip: str, dest_port: int, src_port: int, hostname: str, sleeptime: int, start_w_token: bool):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_ip = dest_ip
        self.hostname = hostname
        self.sleeptime = sleeptime
        self.dest_port = dest_port
        self.src_port = src_port
        self.first = start_w_token
        self.closed = False
        self.connect_socket()


    # TODO mexer em todos os metodos abaixo, nenhum eu mexi ainda
    def start(self):
        self.thread_receiver = threading.Thread(
            target=self._start_receive, args=(), daemon=True)
        self.thread_receiver.start()
        time.sleep(1)

    def connect_socket(self):
        source_port = self.socket.getsockname()[1]
        source_ip = self.socket.getsockname()[0]
        self.socket.bind((source_ip, self.so))

    def send_package(self, data: str, dest_port: int):
        if self.closed:
            return
        if "file" in data.split()[0]:
            try:
                readByte = open(data.split()[-1], "rb")
                file_b = readByte.read()
                readByte.close()
                package = (data + " ").encode("utf-8") + file_b
            except FileNotFoundError:
                print("Arquivo nao encontrado, nao foi possivel enviar o pacote.")
                return
        else:
            package = data.encode("utf-8")

        self.socket.sendto(package, (self.dest_ip, dest_port))

    def close_socket(self):
        self.closed = True
        return self.socket.close()

    def _open_package(self, package: tuple) -> str:
        return package[0].decode("utf-8")

    def _create_file(self, filename: str, content: str) -> bool:
        try:
            with open(filename, "w") as file:
                file.write(content)
            return True
        except Exception:
            return False

    def _start_receive(self):
        port = self.socket.getsockname()[1]
        while True:
            print(f"Client is receiving messages on port {port}")
            data = self._open_package(self.socket.recvfrom(1024))
            parts = data.split(" ")
            if '/exit' in data:
                self.close_socket()
                self.disconnect_function(-2)
            elif '/disconnect' in data:
                self.close_socket()
                self.disconnect_function(-3)
            elif '/file' in parts[0]:
                filename = parts[1]
                f_created = self._create_file(
                    filename, content=data.lstrip("/file " + filename))
                if f_created:
                    print("Arquivo criado com sucesso.")
                else:
                    print("Erro ao criar arquivo com connteúdo.")

            else:
                print(f"Nova mensagem de {data}")
