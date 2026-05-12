import pyttsx3
import asyncio
import subprocess

class TTSEngine:
    """
    Engine for Text-to-Speech conversion using pyttsx3.
    """
    def __init__(self, rate=150, volume=1.0):
        self.engine = None
        self.use_powershell_tts = False
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)

            # Try to find a female voice for a 'Jarvis' feel (often voice index 1)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
        except Exception as e:
            # Fallback to PowerShell speech synthesis when pyttsx3/SAPI is unavailable.
            print(f"[Jarvis] pyttsx3 unavailable, falling back to PowerShell TTS: {e}")
            self.engine = None
            self.use_powershell_tts = True

    async def speak(self, text: str):
        """
        Speaks the given text.
        """
        print(f"[Jarvis] Speaking: {text}")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._speak_sync, text)

    def _speak_sync(self, text: str):
        if self.engine is not None:
            self.engine.say(text)
            self.engine.runAndWait()
            return
        if self.use_powershell_tts:
            safe = text.replace("'", "''")
            cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$speak.Speak('{safe}')"
            )
            try:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", cmd],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass
