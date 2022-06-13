
import os
from urllib.parse import urlencode, quote
import asyncio
import pyatv
from pyatv import scan, pair
from pyatv.helpers import is_streamable
from pyatv.const import Protocol


async def play(id, url="F:\Videos\VueJSCrashCourse2021.mp4"):
    loop = asyncio.get_event_loop()

    # Get a configuration with scan
    atvs = await pyatv.scan(loop, identifier=id)

    # Apple TV configuration (first found device in this case)
    conf = atvs[0]

    # Connect with obtained configuration
    atv = await pyatv.connect(atvs[0], loop)

    # Do something
    print(url)
    if is_streamable(url):
        await atv.stream.play_url(url)
    else:
        print("File not playable")

    await asyncio.gather(*atv.close())


if __name__ == "__main__":
    id = "68:64:4B:2B:B7:53"
    url = "F:\Videos\VueJSCrashCourse2021.mp4"
    asyncio.run(play(id, url))  # asyncio.run requires python 3.7+