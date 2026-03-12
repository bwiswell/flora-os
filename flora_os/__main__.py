import asyncio
import sys

from .flora import Flora
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
        flora = await Flora.initialize()
        await flora.run()

if __name__ == '__main__':
    asyncio.run(initialize())