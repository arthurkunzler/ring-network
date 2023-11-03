from enum import Enum


class Answer(Enum):
    naoexiste = 0
    ACK = 1
    NACK = -1


class Prefix(Enum):
    TOKEN = '9000'
    DATA = '7777'
