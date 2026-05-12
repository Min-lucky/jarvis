import pyttsx3
import asyncio

class TTSEngine:
    """
    Engine for Text-to-Speech conversion using pyttsx3.
    """
    def __init__(self, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Try to find a female voice for a 'Jarvis' feel (often voice index 1)
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)

    async def speak(self, text: str):
        """
        Speaks the given text.
        """
        print(f"[Jarvis] Speaking: {text}")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._speak_sync, text)

    def _speak_sync(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
