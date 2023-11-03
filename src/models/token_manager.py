from models.constants import Prefix
from datetime import datetime


class TokenManager:
    def __init__(self, minimum_time: int, timeout: int) -> None:
        self.minimum_time: int = minimum_time  # ms
        self.timeout: int = timeout  # ms
        self.token = None
        self.last_passed_at = None

    def generate_token(self):
        print('Generating token!')
        self.token = Prefix.TOKEN
        self.last_passed_at = datetime.now()
        return self.token

    # Verifica se o comportamento do token é o esperado
    def handle_token(self):
        if self.token is not None:
            if not self.check_timeout():
                print('Token timeout! Need to be regenerated.')
            elif not self._check_minimum_time():
                print('More than one token on network! Need to remove it.')
            else:
                print('Token is OK.')
                self.last_passed_at = datetime.now()
                return True

        return False

    # Calcula quanto tempo passou (em ms) desde que o token foi gerado
    def _time_since_last_pass(self) -> int:
        return int((datetime.now()-self.last_passed_at).total_seconds() * 1000)

    def check_timeout(self):
        if self._time_since_last_pass() > self.timeout:
            return False
        else:
            return True

    def _check_minimum_time(self):
        if self._time_since_last_pass() < self.minimum_time:
            return False
        else:
            return True

    def __repr__(self) -> str:
        if self.token is not None:
            return 'Token {0} - Last pass: {1}, Mininimum time: {2}ms, Timeout: {3}ms'.format(self.token.value, self.last_passed_at, self.minimum_time, self.timeout)
        else:
            return "No token to manage"