import asyncio
from pyatv import scan, pair
from pyatv.const import Protocol

async def main():
    loop = asyncio.get_event_loop()

    atvs = await scan(loop)

    pairing = await pair(atvs[0], Protocol.MRP, loop)
    await pairing.begin()

    if pairing.device_provides_pin:
        pin = int(input("Enter PIN: "))
        pairing.pin(pin)
    else:
        pairing.pin(1234)  # Should be randomized
        input("Enter this PIN on the device: 1234")

    await pairing.finish()

    # Give some feedback about the process
    if pairing.has_paired:
        print("Paired with device!")
        print("Credentials:", pairing.service.credentials)
    else:
        print("Did not pair with device!")

    await pairing.close()

asyncio.run(main())  # asyncio.run requires python 3.7+
