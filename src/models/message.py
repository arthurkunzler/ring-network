class Message:
    def __init__(self, nickname, data):
        self.nickname = nickname
        self.data = data

    def __repr__(self) -> str:
        return 'Apelido: {0}, conteúdo: {1}'.format(self.nickname, self.data)
