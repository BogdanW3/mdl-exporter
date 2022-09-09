from typing import Optional, List

import bpy
from mathutils import Matrix

from .War3AnimationCurve import War3AnimationCurve
from .War3Node import War3Node


class War3Light(War3Node):
    def __init__(self, name: str,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 parent: Optional[str] = None,
                 pivot: List[float] = [0, 0, 0],
                 bindpose: Optional[Matrix] = None):
        super().__init__(name, anim_loc, anim_rot, anim_scale, parent, pivot, bindpose)

    def __init__(self, name: str, pivot: Optional,
                 bindpose: Optional[Matrix] = None):
        War3Node.__init__(self, name, None, None, None, None, pivot, bindpose)
        # def __init__(self, name: str,
        #          anim_loc: Optional[War3AnimationCurve],
        #          anim_rot: Optional[War3AnimationCurve],
        #          anim_scale: Optional[War3AnimationCurve],
        #          parent: Optional[str], pivot: Optional):
        # War3Object.__init__(self, name, anim_loc, anim_rot, anim_scale, parent, pivot)
        self.type: str = 'Cylinder'
        self.intensity: Optional[float] = None
        self.intensity_anim: Optional[War3AnimationCurve] = None
        self.atten_start: Optional[float] = None
        self.atten_start_anim: Optional[War3AnimationCurve] = None
        self.atten_end: Optional[float] = None
        self.atten_end_anim: Optional[War3AnimationCurve] = None
        self.color: Optional[List[float]] = None
        self.color_anim: Optional[War3AnimationCurve] = None
        self.amb_color: Optional[List[float]] = None
        self.amb_color_anim: Optional[War3AnimationCurve] = None
        self.amb_intensity: Optional[float] = None
        self.amb_intensity_anim: Optional[War3AnimationCurve] = None
        # self.bpy_obj: Optional[bpy.types.Object] = None
        self.visibility: Optional[War3AnimationCurve]
