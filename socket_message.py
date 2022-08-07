import socket

from pydis_classes import Disconnect, CommandError, Error

HEADER_LENGTH = 10


class PydisMessage:
    def __init__(self, msg_socket: socket.socket):
        self.msg_socket = msg_socket
        self.w_buffer = msg_socket.makefile('wb')
        self.r_buffer = msg_socket.makefile('rb')
        self.pydis_encoder = PydisEncoding(self.w_buffer, self.r_buffer)

    def send(self, data):
        self.w_buffer.write(data)
        self.w_buffer.flush()

    def send_encoded(self, data):
        self.pydis_encoder.pydis_encode(data)
        self.w_buffer.flush()

    def receive(self) -> bytes:
        return self.r_buffer.readline()

    def receive_decoded(self):
        return self.pydis_encoder.pydis_decode()


class PydisEncoding:
    def __init__(self, w_buffer, r_buffer):
        self.w_buffer = w_buffer
        self.r_buffer = r_buffer
        self.handlers = {
            '+': self.decode_simple_string,
            '-': self.decode_error,
            ':': self.decode_integer,
            '$': self.decode_string,
            '*': self.decode_array,
            '%': self.decode_dict,
        }

    def pydis_decode(self):
        first_byte = self.r_buffer.read(1)
        if not first_byte:
            raise Disconnect()
        try:
            data = self.r_buffer.readline().decode('utf-8').rstrip('\r\n')
            return self.handlers[first_byte.decode('utf-8')](data)
        except KeyError:
            raise CommandError('Bad request.')

    def decode_simple_string(self, data):
        return data

    def decode_error(self, data):
        return Error(data)

    def decode_integer(self, data):
        return int(data)

    def decode_string(self, data):
        length = int(data)
        if length == -1:
            return None
        length += 2
        return self.r_buffer.read(length)[:-2]

    def decode_array(self, data):
        n_elems = int(data)
        return [self.pydis_decode() for _ in range(n_elems)]

    def decode_dict(self, data):
        n_items = int(data)
        elems = [self.pydis_decode() for _ in range(n_items * 2)]
        return dict(zip(elems[::2], elems[1::2]))

    def pydis_encode(self, data):
        if isinstance(data, str):
            self.w_buffer.write(f'+{data}\r\n'.encode('utf-8'))
        elif isinstance(data, bytes):
            self.w_buffer.write(f'${len(data)}\r\n{data}\r\n'.encode('utf-8'))
        elif isinstance(data, int):
            self.w_buffer.write(f':{data}\r\n'.encode('utf-8'))
        elif isinstance(data, Error):
            self.w_buffer.write(f'-{data.message}\r\n'.encode('utf-8'))
        elif isinstance(data, (list, tuple)):
            self.w_buffer.write(f'*{len(data)}\r\n'.encode('utf-8'))
            for item in data:
                self.pydis_encode(item)
        elif isinstance(data, dict):
            self.w_buffer.write(f'%{len(data)}\r\n'.encode('utf-8'))
            for key in data:
                self.pydis_encode(key)
                self.pydis_encode(data[key])
        elif data is None:
            self.w_buffer.write('$-1\r\n'.encode('utf-8'))
        else:
            raise CommandError(f'Unrecognized type: {type(data)}')
