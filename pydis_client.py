import json
import socket

from pydis_classes import Error, CommandError
from socket_message import PydisMessage


class Client:
    def __init__(self, host=socket.gethostname(), port=5050):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.messenger = PydisMessage(self.s)

    def main(self, *input_data):
        if not input_data:
            input_data = input('Enter your message: ').split(' ')
        if input_data[0] == 'exit':
            return True
        if len(input_data) > 3:
            input_data[2] = ' '.join(input_data[2:])
            input_data = input_data[:3]
        if len(input_data) > 2:
            input_data[2] = eval(input_data[2])
        self.messenger.send_encoded(input_data)
        print('Waiting for response message!')
        msg = self.messenger.receive_decoded()
        if isinstance(msg, Error):
            raise CommandError(msg.message)
        print(f'Response from server: {msg}')

    @staticmethod
    def parse_input(input_data: str):
        try:
            return int(input_data)
        except ValueError:
            pass
        try:
            return json.loads(input_data)
        except json.decoder.JSONDecodeError:
            pass
        return input_data

    def loop(self):
        while True:
            try:
                is_break = self.main()
                if is_break:
                    break
            except KeyboardInterrupt:
                print('\nThanks for using our product!')
                exit()
            except CommandError as ce:
                print(ce.args[0])


if __name__ == '__main__':
    client = Client()
    client.loop()
