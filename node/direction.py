import math

class DirectionEstimator:
    def __init__(self, min_history=3):
        self.min_history = min_history

    def analyze(self, track):
        history = track.get('history', [])
        if len(history) < self.min_history:
            return "unknown"
        
        start = history[0]
        end = history[-1]
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        dist = math.hypot(dx, dy)
        if dist < 10:
            return "stationary"
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "approaching" if dy > 0 else "leaving"
