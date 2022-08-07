import socket

from pydis_classes import Error, CommandError
from socket_message import PydisMessage


class Client:
    def __init__(self, host=socket.gethostname(), port=5050):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.messenger = PydisMessage(self.s)

    def _request(self, *args):
        self.messenger.send_encoded(args)
        print('Waiting for response message!')
        msg = self.messenger.receive_decoded()
        if isinstance(msg, Error):
            raise CommandError(msg.message)
        print('Response message received.')
        return msg

    def get(self, key):
        return self._request('GET', key)

    def set(self, key, value):
        return self._request('SET', key, value)

    def delete(self, key):
        return self._request('DELETE', key)

    def flush(self):
        return self._request('FLUSH')

    def mget(self, *keys):
        return self._request('MGET', *keys)

    def mset(self, *items):
        return self._request('MSET', *items)
