import asyncio
import sys

from .network import Client, Server
from .traction import Traction


module = sys.argv[1]


async def initialize ():
    if module == 'traction':
        traction = await Traction.initialize()
        await traction.run()
    elif module == 'sensors':
        await Client.connect('sensors')
    else:
        server = Server()
        await server.wait_for_ready()

if __name__ == '__main__':
    asyncio.run(initialize())