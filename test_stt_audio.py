
import asyncio
import json
import urllib.request
import urllib.error

import sounddevice as sd
import numpy as np
from scipy.signal import resample_poly

from gnani.stt import (
    GnaniSTTStreamClient,
    StreamTranscriptEvent,
    StreamProcessingEvent,
    StreamErrorEvent,
)
from app.config import GNANI_API_KEY

RECORD_RATE = 44100
STT_RATE = 16000
DURATION = 8
CHUNK_SIZE = 1024

API_URL = "http://127.0.0.1:8002/transactions/voice"


def record_audio():
    print("\nSpeak now! Say: Ramesh paid five rupees.")

    audio = sd.rec(
        int(DURATION * RECORD_RATE),
        samplerate=RECORD_RATE,
        channels=1,
        dtype="int16",
        device=1
    )
    sd.wait()

    print("Recording completed!")
    print("Input peak:", np.max(np.abs(audio.astype("int32"))))

    converted = resample_poly(
        audio[:, 0].astype(np.float32), 160, 441
    )
    converted = np.clip(converted, -32768, 32767).astype("<i2")

    print("Converted samples:", len(converted))
    return converted.tobytes() + b"\x00" * (STT_RATE * 2)


async def audio_chunks(audio_data):
    for position in range(0, len(audio_data), CHUNK_SIZE):
        chunk = audio_data[position:position + CHUNK_SIZE]

        if len(chunk) < CHUNK_SIZE:
            chunk += b"\x00" * (CHUNK_SIZE - len(chunk))

        yield chunk


def save_transaction(transcript):
    payload = json.dumps(
        {"transcript": transcript},
        ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print("\nKHATA TRANSACTION RESULT:")
            print(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        print("\nAPI ERROR:", error.code)
        print(error.read().decode("utf-8"))

    except Exception as error:
        print("\nAPI CONNECTION ERROR:", str(error))


async def main():
    audio_data = record_audio()

    client = GnaniSTTStreamClient(
        api_key=GNANI_API_KEY,
        language_code="en-IN",
        model="prisma-v3.0",
        sample_rate=STT_RATE,
        format="codemix"
    )

    try:
        connection = await client.connect()
        print("\nGnani connected:", connection.message)

        async def sender():
            async for chunk in audio_chunks(audio_data):
                await client.send_audio(chunk)
                await asyncio.sleep(CHUNK_SIZE / 2 / STT_RATE)

        async def receiver():
            async for event in client.events():
                print("\nSERVER EVENT:", type(event).__name__)

                if isinstance(event, StreamTranscriptEvent):
                    print("TRANSCRIPT:", event.text)
                    print("LANGUAGE:", event.detected_language_code)

                elif isinstance(event, StreamProcessingEvent):
                    print("PROCESSING:", event.raw)

                elif isinstance(event, StreamErrorEvent):
                    print("SERVER ERROR:", event.message, event.raw)

        receive_task = asyncio.create_task(receiver())

        await sender()

        print("\nAudio sent. Waiting 8 seconds for Gnani...")
        await asyncio.sleep(8)

        transcripts = list(client._transcripts)
        print("\nCollected transcripts:", len(transcripts))

        transcript = next(
            (
                t.text.strip()
                for t in transcripts
                if any(
                    word in t.text.lower()
                    for word in ("credit", "credited", "debit", "payment", "paid", "pay", "received")
                )
            ),
            ""
        )

        if transcript:
            print("\nSending transcript to Kirana Voice Munim...")
            await asyncio.to_thread(save_transaction, transcript)
        else:
            print("No valid transaction transcript. Nothing saved.")

        if not receive_task.done():
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
    except Exception as error:
        print("\nERROR:", type(error).__name__, str(error))

    finally:
        if client.is_connected:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
