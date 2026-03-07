import asyncio
import sys

from .network import Client, Message, Server
from .sensors import Sensors
from .traction import Traction


module = sys.argv[1]


async def initialize ():
    if module == 'traction':
        traction = await Traction.initialize()
        await traction.run()
    elif module == 'sensors':
        sensors = await Sensors.initialize()
        await sensors.run()
    else:
        server = Server()
        serve = asyncio.create_task(server.serve())
        await server.wait_for_ready()
        await serve

if __name__ == '__main__':
    asyncio.run(initialize())