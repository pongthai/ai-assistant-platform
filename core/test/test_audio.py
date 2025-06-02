import numpy as np
import sounddevice as sd
import webrtcvad

SAMPLE_RATE = 48000
FRAME_DURATION_MS = 30
FRAME_LEN = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # = 480
BLOCKSIZE = FRAME_LEN
AUDIO_DTYPE = 'int16'
CHANNELS = 1
VAD_MODE = 2

vad = webrtcvad.Vad(VAD_MODE)

def audio_callback(indata, frames, time_info, status):
    frame = indata[:, 0]
    if len(frame) >= FRAME_LEN:
        try:
            is_speech = vad.is_speech(frame.tobytes(), SAMPLE_RATE)
            print(f"?? Speech Detected: {is_speech}")
        except Exception as e:
            print("? VAD Error:", e)

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype=AUDIO_DTYPE,
    callback=audio_callback,
    blocksize=BLOCKSIZE,
):
    print("? Listening... Ctrl+C to stop")
    while True:
        sd.sleep(100)
