from typing import Optional, Tuple, Dict

from export_mdl.alt_classes.ComponentTransform import ComponentTransform


class GeosetAnim:
    def __init__(self):
        self.color: Optional[Tuple[float]]
        self.alpha: float = 1.0
        self.transforms: Dict[str, ComponentTransform] = {}

