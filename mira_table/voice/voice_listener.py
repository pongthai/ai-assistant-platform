import webrtcvad
import sounddevice as sd
import numpy as np
import queue
import threading
import collections
import time
import logging
import struct
import speech_recognition as sr

logger = logging.getLogger(__name__)

SAMPLE_RATE = 48000
FRAME_DURATION = 30

class VADVoiceListener:
    def __init__(self, aggressiveness=2, sample_rate=SAMPLE_RATE, frame_duration=FRAME_DURATION):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.frame_bytes = self.frame_size * 2  # 16-bit audio
        self.audio_queue = queue.Queue()
        self.running = False

    def _callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"VAD stream status: {status}")
        self.audio_queue.put(bytes(indata))

    def _record_and_detect(self):
        ring_buffer = collections.deque(maxlen=10)
        triggered = False
        voiced_frames = []
        silence_counter = 0

        with sd.RawInputStream(samplerate=self.sample_rate,
                               blocksize=self.frame_size,
                               dtype='int16',
                               channels=1,
                               callback=self._callback):
            logger.info("[VAD] Listening for voice...")

            while self.running:
                try:
                    frame = self.audio_queue.get(timeout=1)
                    is_speech = self.vad.is_speech(frame, self.sample_rate)
                    
                    if not triggered:
                        ring_buffer.append((frame, is_speech))
                        num_voiced = len([f for f, speech in ring_buffer if speech])
                        if num_voiced > 0.8 * ring_buffer.maxlen:
                            triggered = True
                            logger.info("[VAD] Voice detected")
                            voiced_frames.extend(f for f, s in ring_buffer)
                            ring_buffer.clear()
                    else:
                        voiced_frames.append(frame)
                        if not is_speech:
                            silence_counter += 1
                        else:
                            silence_counter = 0

                        if silence_counter > 6:
                            logger.info("[VAD] Voice ended")
                            break

                except queue.Empty:
                    continue

        audio_data = b''.join(voiced_frames)
        return audio_data

    def listen_and_recognize(self, language="th-TH"):
        self.running = True
        audio_bytes = self._record_and_detect()
        self.running = False

        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(audio_bytes, self.sample_rate, sample_width=2)

        try:
            text = recognizer.recognize_google(audio_data, language=language)
            logger.info(f"[VAD] Recognized: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("[VAD] Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"[VAD] Speech recognition error: {e}")
            return None