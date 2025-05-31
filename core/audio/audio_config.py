# audio_config.py
# -*- coding: utf-8 -*-
import sounddevice as sd
import os

def list_all_devices():
    devices = sd.query_devices()
    print("\n🎧 Available Audio Devices:\n")
    for idx, dev in enumerate(devices):
        io_info = []
        if dev['max_input_channels'] > 0:
            io_info.append(f"{dev['max_input_channels']} in")
        if dev['max_output_channels'] > 0:
            io_info.append(f"{dev['max_output_channels']} out")
        io_str = ", ".join(io_info)
        print(f"{idx:>3}: {dev['name']} ({io_str})")

list_all_devices()

# อ่าน mic_id และ speaker_id จาก environment variables
mic_id = int(os.getenv("MIC_ID", -1))
speaker_id = int(os.getenv("SPEAKER_ID", -1))

if mic_id >= 0 and speaker_id >= 0:
    sd.default.device = (mic_id, speaker_id)
    print(f"\n✅ Audio input/output devices set: mic_id={mic_id}, speaker_id={speaker_id}")
else:
    print("\n⚠️  MIC_ID and/or SPEAKER_ID not set or invalid. Please define them in environment variables.")
