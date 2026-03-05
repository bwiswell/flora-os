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
        Server()
        await asyncio.sleep(20)

if __name__ == '__main__':
    asyncio.run(initialize())