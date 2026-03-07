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
        server = await Server.connect()
        print('backwards...')
        await server.write(Message.move(-0.7, -0.7))
        await asyncio.sleep(5)
        print('forwards...')
        await server.write(Message.move(0.7, 0.7))
        await asyncio.sleep(5)
        print('stopping...')
        await server.write(Message.stop())
        await asyncio.sleep(5)
        print('closing...')
        await server.close()
        server.join()

if __name__ == '__main__':
    #asyncio.run(initialize())
    test()