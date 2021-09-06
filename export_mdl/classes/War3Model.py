from collections import defaultdict
from typing import List, Dict

import bpy

from .War3Geoset import War3Geoset
from .War3GeosetAnim import War3GeosetAnim
from .War3Material import War3Material
from .War3Object import War3Object


class War3Model:

    default_texture = "Textures\white.blp"
    decimal_places = 5

    def __init__(self, context: bpy.context):
        self.objects = defaultdict(set)
        self.objects_all: List[War3Object] = []
        self.object_indices: Dict[str, int] = {}
        self.geosets: List[War3Geoset] = []
        self.geoset_map = {}
        self.geoset_anims: [War3GeosetAnim] = []
        self.geoset_anim_map = {}
        self.materials: [War3Material] = []
        self.sequences = []
        self.global_extents_min = 0
        self.global_extents_max = 0
        self.const_color_mats = set()
        self.global_seqs = set()
        self.cameras = []
        self.textures = []
        self.tvertex_anims = []

        self.f2ms = 1000 / context.scene.render.fps  # Frame to millisecond conversion
        self.name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")
