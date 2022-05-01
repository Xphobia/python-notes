#!/usr/bin/env python

import subprocess
import time

import nonblock

test_commands = [
    'ping',
    'ping -c 8 127.0.0.1',
    'tcpdump port 22'
]


def test_nonblock(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        time.sleep(1)
        error = nonblock.nonblock_read(process.stderr)
        if not error:
            break
        else:
            print("command: %s error==>" % command)
            print(error)

    line = ''
    while True:
        time.sleep(0.5)
        output = nonblock.nonblock_read(process.stdout, 256)
        if output is None:
            break
        if output:
            idx = output.find("\n")
            if idx == -1:
                line += output
            else:
                line += output[:idx]
                print(line.strip())
                line = output[idx:]
        else:
            print('nothing to read !')


def test_block(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = process.communicate()

    import os
    import fcntl
    fd = process.stdout
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    while True:
        time.sleep(0.5)
        error = process.stderr.read()
        if not error:
            break
        else:
            print("command: %s error==>" % command)
            print(error)
            return

    while process.poll() is not None:
        time.sleep(0.5)
        line = process.stdout.readline()
        if line:
            print(line.strip())
        else:
            print('nothing to read')
            break


def main():
    for command in test_commands:
        print('======start test command: %s======' % command)
        test_block(command)
        # test_nonblock(command)
        print('======finish test command: %s======' % command)


if __name__ == '__main__':
    main()
