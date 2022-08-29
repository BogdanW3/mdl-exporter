from typing import Dict

from export_mdl.alt_classes.SequenceTrack import SequenceTrack


class ComponentTransform:
    def __init__(self, transform_type: str):
        self.transform_type: str = transform_type
        self.interpolation = 'Linear'
        self.keyframes: Dict[str, SequenceTrack] = {}
