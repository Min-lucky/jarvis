import pyaudio
import numpy as np
from collections import deque

class AudioCapture:
    """Continuously reads audio from the default microphone.
    Produces chunks of float32 samples in the range [-1.0, 1.0]."""
    def __init__(self, rate: int = 44100, chunk: int = 1024):
        self.rate = rate
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        
        try:
            # Get default input device info
            default_device = self.p.get_default_input_device_info()
            print(f"DEBUG: Using Audio Device: {default_device['name']} (Index: {default_device['index']})")
            
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )
        except OSError as e:
            print(f"CRITICAL ERROR: Could not open audio stream. Error: {e}")
            print("TIP: Check your Windows Privacy Settings -> Microphone -> 'Allow apps to access your microphone'")
            raise
            
        self.buffer = deque(maxlen=self.rate * 5)  # keep up to 5 seconds

    def read(self) -> np.ndarray:
        """Read a chunk and append to internal buffer. Returns the chunk as a NumPy array."""
        try:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.float32)
            self.buffer.extend(samples)
            return samples
        except Exception as e:
            print(f"ERROR: Audio read failed: {e}")
            return np.zeros(self.chunk, dtype=np.float32)

    def get_buffer(self) -> np.ndarray:
        """Return the whole circular buffer as a NumPy array."""
        return np.array(self.buffer, dtype=np.float32)

    def close(self):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
