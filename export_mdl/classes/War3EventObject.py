from typing import Optional, List

from mathutils import Matrix

from .War3AnimationCurve import War3AnimationCurve
from .War3Node import War3Node


class War3EventObject(War3Node):
    def __init__(self, name: str,
                 obj_id: int = -1,
                 pivot: List[float] = [0, 0, 0],
                 parent_id: Optional[int] = None,
                 parent: Optional[str] = None,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 bindpose: Optional[Matrix] = None):
        super().__init__(name, obj_id, pivot, parent_id, parent, anim_loc, anim_rot, anim_scale, bindpose)
        self.track: Optional[War3AnimationCurve] = None

    @classmethod
    def create_from(cls, node: 'War3Node'):
        return War3EventObject(node.name, node.obj_id, node.pivot,
                               node.parent_id, node.parent,
                               node.anim_loc, node.anim_rot, node.anim_scale,
                               node.bindpose)
