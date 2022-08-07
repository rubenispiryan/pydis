from pydis_classes import CommandError


class PydisMemory:
    def __init__(self):
        self._kv = {}
        self._commands = {
            'GET': self._get,
            'SET': self._set,
            'DELETE': self._delete,
            'FLUSH': self._flush,
            'MGET': self._mget,
            'MSET': self._mset
        }

    def get_response(self, data):
        if not isinstance(data, list):
            try:
                data = data.split()
            except Exception:
                raise CommandError('Request must be list or simple string.')

        if not data:
            raise CommandError('Missing command')

        command = data[0].upper()
        if command not in self._commands:
            raise CommandError(f'Unrecognized command: {command}')
        else:
            print('Received: ' + command)
        print(f'Creating a command request with following data:\nCommand: {data}')
        return self._commands[command](*data[1:])

    def _get(self, key):
        return self._kv.get(key)

    def _set(self, key, value):
        self._kv[key] = value
        return 1

    def _delete(self, key):
        if key in self._kv:
            del self._kv[key]
            return 1
        return 0

    def _flush(self):
        kvlength = len(self._kv)
        self._kv.clear()
        return kvlength

    def _mget(self, *keys):
        return [self._kv.get(key) for key in keys]

    def _mset(self, *items):
        data = zip(items[::2], items[1::2])
        for key, value in data:
            self._kv[key] = value
        return len(items) // 2
