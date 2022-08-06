import socket
from time import sleep

from port_util import free_port
from pydis_classes import Disconnect, CommandError, Error
from pydis_memory import PydisMemory
from socket_message import PydisMessage

PORT = 5050


def main():
    free_port(PORT)
    sleep(0.1)

    print('\n' + '-' * 10 + 'MAIN' + '-' * 10 + '\n')
    pydis = PydisMemory()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((socket.gethostname(), PORT))

    s.listen(5)

    client, address = s.accept()
    print(f'New connection from {address}')
    while True:
        client_messenger = PydisMessage(client)
        print('Waiting for new message!')
        msg = client_messenger.receive_decoded()
        print(msg)
        if len(msg) == 0:
            raise Disconnect()
        print(f'Received message from client: {msg}')
        try:
            response_message = pydis.get_response(msg)
        except CommandError as ce:
            response_message = Error(ce.args[0])
        client_messenger.send_encoded(response_message)
        print(f'Response sent: {response_message}')


if __name__ == '__main__':
    try:
        main()
    except Disconnect:
        print('User disconnected.')
