import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

_executor = ThreadPoolExecutor()


async def cpu_bound_task(func: Callable, *args):
    """
    Execute async function in a separate thread, without blocking the main event
    loop.

    :param func: async function that will be executed in separate thread
    :param args: async function parameters
    :return: async function result
    """
    return await asyncio.get_event_loop().run_in_executor(
        _executor, func, *args)
