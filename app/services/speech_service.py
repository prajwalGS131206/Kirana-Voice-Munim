import asyncio
from gnani.stt import GnaniSTTStreamClient
from app.config import GNANI_API_KEY


def create_stt_client():
    return GnaniSTTStreamClient(
        api_key=GNANI_API_KEY,
        language_code="indic-auto",
        model="prisma-v3.0",
        sample_rate=16000,
        format="codemix"
    )


async def connect_stt():
    client = create_stt_client()

    try:
        event = await client.connect()
        print("GNANI STT CONNECTED")
        print("Message:", event.message)
        print("Sample rate:", event.sample_rate)
    finally:
        await client.close()