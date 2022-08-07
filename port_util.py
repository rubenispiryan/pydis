import os
import signal
from subprocess import Popen, PIPE


def free_port(port):
    process = Popen(['lsof', '-i', f':{port}'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(f'Found following processes on port {port}:\n{stdout.decode("utf-8")}')
    for process in str(stdout.decode('utf-8')).split('\n')[1:]:
        data = [x for x in process.split(' ') if x != '']
        if len(data) <= 1:
            continue
        os.kill(int(data[1]), signal.SIGKILL)
        print(f'Successfully killed proces: {data[0]} with PID: {data[1]}')
