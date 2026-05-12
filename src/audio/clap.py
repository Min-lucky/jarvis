import numpy as np
import time

class ClapDetector:
    """Detect a double‑clap within a configurable time window.
    Improved version using peak amplitude and cooldowns.
    """

    def __init__(self, threshold: float = 0.3, max_interval: float = 1.5):
        self.threshold = threshold
        self.max_interval = max_interval
        self.last_clap_time: float | None = None
        self.cooldown = 0.2  # Minimum seconds between individual claps

    def feed(self, samples: np.ndarray) -> bool:
        """Feed a block of audio samples.
        Returns ``True`` when a double‑clap has been detected.
        """
        # Use peak absolute value for transient detection
        peak = float(np.max(np.abs(samples)))
        
        if peak > self.threshold:
            now = time.time()
            
            # Check for cooldown to avoid multiple detections of the same clap
            if self.last_clap_time is not None:
                interval = now - self.last_clap_time
                if interval < self.cooldown:
                    return False
                
                if interval <= self.max_interval:
                    # Double clap detected!
                    print(f"DEBUG: Double clap detected (interval: {interval:.2f}s)")
                    self.last_clap_time = None # Reset for next detection
                    return True
            
            # First clap (or interval too long)
            print(f"DEBUG: Single clap detected (peak: {peak:.2f})")
            self.last_clap_time = now
            
        return False
