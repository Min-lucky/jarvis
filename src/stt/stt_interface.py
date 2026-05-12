import asyncio
import numpy as np
import speech_recognition as sr

class STTInterface:
    """
    Interface for Speech-to-Text conversion.
    Supports both a placeholder console input and real voice recognition.
    """
    def __init__(self, backend="placeholder"):
        self.backend = backend
        self.recognizer = sr.Recognizer()

    async def transcribe(self, audio_data: np.ndarray = None, sample_rate: int = 44100) -> str:
        """
        Transcribes audio data to text.
        """
        if self.backend == "placeholder":
            print("\n[Jarvis] Listening... (Placeholder: please type your command below)")
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, input, "You: ")
            return text.strip()
        else:
            loop = asyncio.get_event_loop()
            if audio_data is not None and len(audio_data) > 0:
                return await loop.run_in_executor(None, self._transcribe_from_samples, audio_data, sample_rate)
            # Fallback to direct microphone capture when no samples are provided.
            print("\n[Jarvis] Listening to your voice...")
            return await loop.run_in_executor(None, self._listen_and_transcribe)

    def _transcribe_from_samples(self, samples: np.ndarray, sample_rate: int = 44100):
        """Transcribe float32 samples in range [-1, 1] using recognizer backend."""
        try:
            clipped = np.clip(samples, -1.0, 1.0)
            pcm16 = (clipped * 32767.0).astype(np.int16)
            audio = sr.AudioData(pcm16.tobytes(), sample_rate=sample_rate, sample_width=2)
            print("[Jarvis] Processing voice...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("[Jarvis] Sorry, I didn't catch that.")
            return ""
        except Exception as e:
            print(f"[Jarvis] Voice Error: {str(e)}")
            return ""

    def _listen_and_transcribe(self):
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("[Jarvis] Processing voice...")
                # Using Google Speech Recognition as a default free backend
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                print("[Jarvis] Listening timed out.")
                return ""
            except sr.UnknownValueError:
                print("[Jarvis] Sorry, I didn't catch that.")
                return ""
            except Exception as e:
                print(f"[Jarvis] Voice Error: {str(e)}")
                return ""
