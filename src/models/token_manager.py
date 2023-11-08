import models.constants as Constants
from datetime import datetime


class TokenManager:
    def __init__(self, minimum_time: int, timeout: int) -> None:
        self.minimum_time: int = minimum_time  # ms
        self.timeout: int = timeout  # ms
        self.token = None
        self.last_passed_at = None
        self.has_timeout = False
        self.more_tokens = False

    def generate_token(self):
        self.token = Constants.Prefix.TOKEN
        self.last_passed_at = datetime.now()
        print(Constants.TOKEN_GENERATED)
        print(self)
        return self.token

    # Verifica se o comportamento do token é o esperado
    def handle_token(self, tkn=None):
        if not self.check_timeout():
            self.has_timeout = True
            print(Constants.TIMEOUT_MESSAGE)
            return False
        elif not self._check_minimum_time():
            self.more_tokens = True
            print(Constants.MORE_THAN_ONE_TOKEN)
            return False
        else:
            print(Constants.TOKEN_OK)
            self.last_passed_at = datetime.now()
            # Recebemos o token
            if tkn is not None:
                self.token = tkn

        return True

    # Calcula quanto tempo passou (em ms) desde que o token foi gerado
    def _time_since_last_pass(self) -> int:
        return int((datetime.now()-self.last_passed_at).total_seconds() * 1000)

    def check_timeout(self):
        if (self.token is None and self.timeout > 0 and self._time_since_last_pass() > self.timeout):
            print(Constants.TIMEOUT_MESSAGE)
            return False
        else:
            return True

    def _check_minimum_time(self):
        if (self.minimum_time > 0 and self._time_since_last_pass() < self.minimum_time):
            return False
        else:
            return True

    def __repr__(self) -> str:
        return f"""
{Constants.Style.OKBLUE}
Token Manager;
Last pass: {self.last_passed_at};
Mininimum time: {self.minimum_time}ms;
Timeout: {self.timeout}ms;
Control information:
    Has timeout: {self.has_timeout};
    Has another token: {self.more_tokens}.
{Constants.Style.ENDC}
"""
