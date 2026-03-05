import sys

from .network import Client, Server


module = sys.argv[1]


if __name__ == '__main__':
    if module == 'traction':
        Client.connect('traction')
    elif module == 'sensors':
        Client.connect('sensors')
    else:
        Server()