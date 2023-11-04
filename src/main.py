from models.app import App
from models.constants import INVALID_OPTION, MENU, NOT_MANAGER, CONFIG_FILE, SOURCE_PORT, INVALID_CONFIG


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
        time = int(lines[2].strip()) * 1000
        start_w_token = lines[3].strip()
        if start_w_token == "true":
            start_w_token = True
        else:
            start_w_token = False
    return ip, port, hostname, time, start_w_token


def run_client(app: App):
    app.start()
    while not app.closed:
        app.check_token_timeout()
        handle_choice(app, handle_menu())
        # TODO fazer loop para cliente escrever mensagens e enviar com app.send_package()


def handle_choice(app: App, choice: int):
    if choice == 0:
        # TODO tratar o envio de mensagem
        pass
    elif choice == 1:
        # TODO printar status
        pass
    elif choice == 2:
        if not app.is_token_manager:
            print(NOT_MANAGER)
        else:
            print(app.token_manager)


def handle_menu() -> int:
    valid = False
    while not valid:
        print(MENU)
        choice = int(input())
        valid = choice >= 0 and choice <= 2
        if not valid:
            print(INVALID_OPTION)

    return choice


def main():
    dest_ip, port, hostname, timeout, start_w_token = parse_config_file(
        file=CONFIG_FILE)
    print(f"IP {dest_ip} port {port} hostname {hostname} token_time {timeout} start {start_w_token}")
    # Add parâmetros relativos ao gerenciamento de token
    app = App(dest_ip=dest_ip, dest_port=port, src_port=SOURCE_PORT,
              hostname=hostname, is_token_manager=start_w_token, timeout_token=timeout)

    run_client(app=app)


if __name__ == "__main__":
    main()
