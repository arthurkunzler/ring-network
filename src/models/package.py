class Package:
    def __init__(self, data: str):
        self.type = None
        self.error_control = None
        self.origin_name = None
        self.dest_name = None
        self.crc = None
        self.text = None
        self._split_data(data)

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
        self.type = data[0]
        if len(parts) > 1:
            msg = data[1].split(";")
            self.error_control = msg[0]
            self.origin_name = msg[1]
            self.dest_name=  msg[2]
            self.crc = msg[3]
            self.text = msg[4:]
