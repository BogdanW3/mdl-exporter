from typing import Dict, List, Tuple


class SequenceTrack:
    def __init__(self):
        self.sequence: str
        self.interpolation = 'Linear'
        self.times: List[float] = []
        self.keyframes: Dict[float, Tuple[float]] = {}
        self.handles_right: Dict[float, Tuple[float]] = {}
        self.handles_left: Dict[float, Tuple[float]] = {}

