from typing import Optional, Dict, List, Tuple

from mathutils import Vector

from export_mdl.alt_classes.ComponentTransform import ComponentTransform
from export_mdl.alt_classes.Sequence import Sequence


class Node:
    def __init__(self, name: str):
        self.name: str = name
        self.parent: Optional[Node]
        self.pivot: Vector = Vector([0.0, 0.0, 0.0])
        self.transforms: Dict[Sequence, ComponentTransform] = {}
        self.billboarded: bool = False
        self.billboard_lock: Tuple[bool, bool, bool] = (False, False, False)
        self.bindpose: Optional[List[float]] = None
