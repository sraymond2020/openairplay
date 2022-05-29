import os
from urllib.parse import urlencode, quote
import asyncio
import pyatv
from pyatv import scan, pair
from pyatv.const import Protocol

localDirectory = os.getcwd()
print(localDirectory)

async def main():
    loop = asyncio.get_event_loop()

    # Get a configuration with scan
    atvs = await pyatv.scan(loop, identifier="68644B2BB753")

    # Apple TV configuration (first found device in this case)
    conf = atvs[0]

    # Connect with obtained configuration
    atv = await pyatv.connect(atvs[0], loop)

    # Do something
    
    # url = os.path.join("C:","Users","Shaun","Videos","Captures","eFootball 2022 2022-05-15 02-32-37.mp4")
    # url = "F:\Videos\How to run TrueNAS on Proxmox.mp4"
    url = "F:\Videos\VueJSCrashCourse2021.mp4"
    # url = "F:\Videos\Vue JS Crash Course 2021.mp4"
    # url = "F:\Videos\iptables - Packet Processing.mp4"
    # url = r"C:\Users\Shaun\Desktop\test folder\123.mp4"
    # url = r"C:\Users\Shaun\Desktop\BigBuckBunny.mp4"
    # url = r"C:\Users\Shaun\Desktop\test folder\BigBuckBunny.mp4"
    # url2 = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    # print(quote(url2))

    # url = url.replace(" ","\ ")
    # url = url.replace("-","\-")
    # url = urlencode(url)

    print(url)
    path, fname = os.path.split(url)
    print("PATH --> ", path)
    os.chdir(path)
    # fname = quote(fname)
    print("File Name -->", fname)

    await atv.stream.play_url(fname)

    atv.close()
    await asyncio.gather(*atv.close())
    os.chdir(localDirectory)


asyncio.run(main())  # asyncio.run requires python 3.7+

info = """
       Name: Living Room Apple TV
   Model/SW: Apple TV 3, ATV SW 8.4.4
    Address: 192.168.1.99
        MAC: 68:64:4B:2B:B7:53
 Deep Sleep: False
Identifiers:
 - 68:64:4B:2B:B7:53
 - C8BBAA43EE8A6980
 - 68644B2BB753
Services:
 - Protocol: AirPlay, Port: 7000, Credentials: None, Requires Password: False, Password: None, Pairing: NotNeeded
 - Protocol: DMAP, Port: 3689, Credentials: 00000000-0d50-828b-c7a3-b254dfc944cd, Requires Password: False, Password: None, Pairing: Optional
 - Protocol: RAOP, Port: 7000, Credentials: None, Requires Password: False, Password: None, Pairing: NotNeeded
 """

