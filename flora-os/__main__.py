import asyncio
import sys

from .network import Server
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
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(initialize())