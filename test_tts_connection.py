import asyncio
from dotenv import load_dotenv
from gnani.tts import GnaniTTSRealtimeClient

load_dotenv()

async def main():
    client = GnaniTTSRealtimeClient()

    try:
        audio = await client.synthesize_and_collect(
            text="Namaskara! Welcome to Kirana Voice Munim.",
            voice="Avinash",
            model="timbre-v3.0",
            language="en-IN"
        )

        with open("test_tts.wav", "wb") as f:
            f.write(audio)

        print("TTS SUCCESS")
        print("Audio bytes:", len(audio))
        print("Saved: test_tts.wav")

    except Exception as e:
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR DETAILS:", repr(e))

asyncio.run(main())