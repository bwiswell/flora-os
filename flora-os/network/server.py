from __future__ import annotations

import asyncio
from typing import Optional

from .io import IO
from .message import Message
from .relay import Relay


class Server(IO):

    INTERRUPT = 0.3

    def __init__ (self, name: str = 'flora'):
        IO.__init__(self, name)
        self.incoming: asyncio.Queue[Message] = asyncio.Queue()
        self.outgoing: asyncio.Queue[Message] = asyncio.Queue()
        self.relays: dict[str, Relay] = {}
        self.dispatch: asyncio.Task = None
        self.server: asyncio.Task = None
        self.serving = False


    ### CLASS METHODS ###
    @classmethod
    async def connect (cls, name: str = 'flora') -> Server:
        server = Server(name)
        await server._serve()
        await server.wait_for_ready()
        return server



    ### HELPERS ###
    async def _dispatch (self):
        while self.serving:
            msg = await self.outgoing.get()
            relay = self.relays[msg.dest]
            await relay.write(msg)
            self.outgoing.task_done()
            await asyncio.sleep(Server.INTERRUPT)

    async def _serve (self):
        self.serving = True
        server = await asyncio.start_server(self._serve_client, port = IO.PORT)
        self.dispatch = asyncio.create_task(self._dispatch())
        self.server = asyncio.create_task(server.serve_forever())
        print(f'server listening on port {IO.PORT}')

    async def _serve_client (
                self,
                reader: asyncio.StreamReader,
                writer: asyncio.StreamWriter
            ):
        relay = Relay(reader, writer)
        src: str = None
        try:
            init = await relay.wait_for_get()
            src = init.src
            print(f'{src} module connected')
            self.relays[src] = relay
            while self.serving:
                msg = await relay.read()
                if msg is not None:
                    await self.incoming.put(msg)
                await asyncio.sleep(Server.INTERRUPT)
        except Exception as e:
            print(e)
        finally:
            if src and src in self.relays:
                self.relays.pop(src)
            await relay.close()

    async def wait_for_ready (self):
        while len(self.relays) < 2:
            print('waiting for modules to connect...')
            asyncio.sleep(5)
        print('starting FLORA...')


    ### METHODS ###
    async def close (self):
        print('broadcasting exit message...')
        await self.write(Message.exit('sensors'))
        await self.write(Message.exit('traction'))
        print('waiting for modules to exit...')
        await asyncio.sleep(3)
        self.serving = False
        print('cancelling server and dispatch tasks...')
        if self.server:
            self.server.cancel()
        if self.dispatch:
            self.dispatch.cancel()
        print('closing client connections...')
        for relay in self.relays.values():
            await relay.close()
        print('server closed')

    async def read (self) -> Optional[Message]:
        try:
            msg = self.incoming.get_nowait()
            # TODO: shift task_done to after processing?
            self.incoming.task_done()
            return msg
        except Exception as e:
            return None
    
    async def write (self, msg: Message):
        await self.outgoing.put(msg)