from models.app import App
from models.token_manager import TokenManager
from models.constants import INVALID_OPTION, MENU, NOT_MANAGER, CONFIG_FILE, ONLINE_MACHINES, SOURCE_PORT, INVALID_CONFIG, EXIT_APP_MESSAGE

# Faz o parse do arquivo de configuração


def parse_config_file(file: str):
    with open(file, "r") as file:
        lines = file.readlines()
        if len(lines) < 4:
            print(INVALID_CONFIG)
            exit(1)
        addresses = lines[0].strip().split(":")
        ip = addresses[0]
        port = addresses[1]
        hostname = lines[1].strip()
        time = int(lines[2].strip()) * 1000  # transforma em ms
        start_w_token = lines[3].strip()
        if start_w_token == "true":
            start_w_token = True
        else:
            start_w_token = False
    return ip, port, hostname, time, start_w_token

# Roda o App


def run_client(app: App):
    app.start()
    while not app.closed:
        try:
            app.check_token_timeout()
            app.send_message()
            handle_choice(app, handle_menu())
        except KeyboardInterrupt as e:
            print(EXIT_APP_MESSAGE)
            app.close_socket()

# Processa a escolha do usuário


def handle_choice(app: App, choice: int):
    if choice == 0:
        dest_name = ''
        while not dest_name:
            print('Insira o destino:')
            dest_name = input()
        message = ''
        while not message:
            print('Insira a mensagem')
            message = input()
        app.add_message(dest_name=dest_name, message=message)

    elif choice == 1:
        print(app.app_status())
    elif choice == 2:
        if not app.is_token_manager:
            print(NOT_MANAGER)
        else:
            print(app.token_manager)
    elif choice == 3:
        app.generate_token()
    elif choice == 4:
        app.remove_token()

# Exibe o menu e lê a opção


def handle_menu() -> int:
    valid = False
    while not valid:
        print(MENU)
        choice = int(input())
        valid = choice >= 0 and choice <= 4
        if not valid:
            print(INVALID_OPTION)

    return choice


def main():
    dest_ip, port, hostname, sleep, start_w_token = parse_config_file(
        file=CONFIG_FILE)
    print(
        f"IP {dest_ip} port {port} hostname {hostname} token_time {sleep} start {start_w_token}")
    # Add parâmetros relativos ao gerenciamento de token
    timeout = (sleep * ONLINE_MACHINES) * 1.15
    token_mng = TokenManager(
        minimum_time=0, timeout=timeout)
    # instancia nova App (host da rede)
    app = App(dest_ip=dest_ip, dest_port=port, src_port=SOURCE_PORT,
              hostname=hostname, is_token_manager=start_w_token, sleep_time=(sleep/1000), token_manager=token_mng)

    run_client(app=app)


if __name__ == "__main__":
    main()
