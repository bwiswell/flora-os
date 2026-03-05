import asyncio
import sys

from .network import Client, Server


module = sys.argv[1]


async def initialize ():
    if module == 'traction':
        await Client.connect('traction')
    elif module == 'sensors':
        await Client.connect('sensors')
    else:
        server = Server()
        await server.wait_for_ready()

if __name__ == '__main__':
    asyncio.run(initialize())