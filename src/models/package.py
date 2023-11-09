from models.constants import ErrorControl, Prefix, Style


class Package:
    def __init__(self, data: str):
        self.type = None
        self.error_control: ErrorControl = None
        self.origin_name = None
        self.dest_name = None
        self.crc = None
        self.text = None
        self._split_data(data)

    def cool_message(self):
        return f"Mensagem: {Style.OKCYAN}{Style.BOLD}{self.text}{Style.ENDC}"

    def __repr__(self) -> str:
        return f"""
Type: '{self.type}';
Error Control: '{self.error_control}';
Origin_name: {self.origin_name};
Destination_name: {self.dest_name};
CRC: {self.crc};
Text: {self.text}.
        """

    # Atribui os campos conforme o tipo da mensagem
    def _split_data(self, data: str):
        parts = data.split(":")
        if parts[0] == Prefix.TOKEN.value:
            self.type = Prefix.TOKEN
            self.text = Prefix.TOKEN.value
        elif parts[0] == Prefix.DATA.value:
            self.type = Prefix.DATA

        if len(parts) > 1:
            msg = parts[1].split(";")
            print(f"AQUII {msg[0]}")
            if msg[0].strip() is ErrorControl.ACK.value:
                self.error_control = ErrorControl.ACK
            elif msg[0].strip() is ErrorControl.NACK.value:
                self.error_control = ErrorControl.NACK
            else:
                self.error_control = ErrorControl.NAOEXISTE

            self.origin_name = msg[1]
            self.dest_name = msg[2]
            self.crc = int(msg[3])
            self.text = "".join(msg[4:])
