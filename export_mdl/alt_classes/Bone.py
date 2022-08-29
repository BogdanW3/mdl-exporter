from typing import Optional, Dict, List, Tuple

from mathutils import Vector

from export_mdl.alt_classes.ComponentTransform import ComponentTransform
from export_mdl.alt_classes.Node import Node


class Bone(Node):
    def __init__(self, name: str):
        super().__init__(name)
