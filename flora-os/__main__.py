import asyncio
import sys

from .network import Client, Message, Server
from .traction import Traction


module = sys.argv[1]


async def initialize ():
    if module == 'traction':
        traction = await Traction.initialize()
        await traction.run()
    elif module == 'sensors':
        await Client.connect('sensors')
        await asyncio.sleep(60)
    else:
        server = await Server.connect()
        print('backwards...')
        await server.write(Message.move(-0.2, -0.2))
        await asyncio.sleep(5)
        print('forwards...')
        await server.write(Message.move(0.2, 0.2))
        await asyncio.sleep(5)
        print('stopping...')
        await server.write(Message.stop())
        await asyncio.sleep(5)
        print('closing...')
        await server.close()
        server.join()

if __name__ == '__main__':
    asyncio.run(initialize())