import asyncio
from dotenv import load_dotenv
from gnani.stt import GnaniSTTStreamClient

load_dotenv()

async def main():
    client = GnaniSTTStreamClient(
        language_code="indic-auto",
        model="prisma-v3.0",
        sample_rate=16000,
        format="codemix"
    )

    try:
        event = await client.connect()
        print("CONNECTED:", event)
    except Exception as e:
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR DETAILS:", repr(e))
    finally:
        await client.close()

asyncio.run(main())