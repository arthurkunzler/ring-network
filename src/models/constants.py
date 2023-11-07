from enum import Enum


class ErrorControl(Enum):
    NAOEXISTE = "naoexiste"
    ACK = "ACK"
    NACK = "NACK"


class Prefix(Enum):
    TOKEN = '9000'
    DATA = '7777'


BROADCAST_MESSAGE = 'TODOS'


class Style:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# CONFIG_FILE = "config.txt"
CONFIG_FILE = "config_manager.txt"
SOURCE_PORT = 12345

MENU = f"""
{Style.BOLD}
### MENU ###
 0- Add Message to queue;
 1- Status;
 2- Token Stats;
 3- Generate Token;
 4- Remove Token;
{Style.ENDC}
"""

INVALID_OPTION = f"""
{Style.FAIL}
{Style.BOLD}
Invalid option! Please a valid option.
{Style.ENDC}
"""

INVALID_CONFIG = f"""
{Style.FAIL}
{Style.BOLD}
Invalid config file. Try again!
{Style.ENDC}
"""

TOKEN_GENERATED  = f"""
{Style.OKBLUE}
{Style.BOLD}
Token has been generated!
{Style.ENDC}
"""

TOKEN_REMOVED  = f"""
{Style.OKCYAN}
{Style.BOLD}
Token removed!
{Style.ENDC}
"""

NOT_MANAGER = f"""
{Style.WARNING}
Host is NOT token manager.
{Style.ENDC}
"""
INVALID_PACKAGE = f"""
{Style.WARNING}
Package received has invalid format.
{Style.ENDC}
"""

TIMEOUT_MESSAGE = f"""
{Style.FAIL}
Token timeout!
{Style.ENDC}
"""