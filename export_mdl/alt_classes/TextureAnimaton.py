from typing import Dict

from export_mdl.alt_classes.ComponentTransform import ComponentTransform
from export_mdl.alt_classes.Sequence import Sequence


class TextureAnimation:
    def __init__(self):
        self.transforms: Dict[Sequence, ComponentTransform] = {}
