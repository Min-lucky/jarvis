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

    async def transcribe(self, audio_data: np.ndarray = None) -> str:
        """
        Transcribes audio data to text.
        """
        if self.backend == "placeholder":
            print("\n[Jarvis] Listening... (Placeholder: please type your command below)")
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, input, "You: ")
            return text.strip()
        else:
            # Real Voice Recognition using speech_recognition
            print("\n[Jarvis] Listening to your voice...")
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._listen_and_transcribe)

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
