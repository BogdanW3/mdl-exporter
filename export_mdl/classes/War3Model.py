from collections import defaultdict
from typing import List, Dict, Tuple, Set, Optional

import bpy

from io_scene_warcraft_3.classes.WarCraft3Texture import WarCraft3Texture
from .War3AnimationAction import War3AnimationAction
from .War3AnimationCurve import War3AnimationCurve
from .War3Attachment import War3Attachment
from .War3Bone import War3Bone
from .War3CollisionShape import War3CollisionShape
from .War3EventObject import War3EventObject
from .War3Geoset import War3Geoset
from .War3GeosetAnim import War3GeosetAnim
from .War3Helper import War3Helper
from .War3Light import War3Light
from .War3Material import War3Material
from .War3Node import War3Node
from .War3ParticleEmitter import War3ParticleEmitter
from .War3ParticleSystem import War3ParticleSystem
from .War3RibbonEmitter import War3RibbonEmitter
from .War3TextureAnim import War3TextureAnim


class War3Model:

    default_texture = "Textures\\white.blp"
    decimal_places = 5

    # def __init__(self, context: bpy.types.Context):
    def __init__(self, name: str):
        self.objects: Dict[str, List[War3Node]] = {}

        self.attachments: List[War3Attachment] = []
        self.bones: List[War3Bone] = []
        self.collision_shapes: List[War3CollisionShape] = []
        self.event_objects: List[War3EventObject] = []
        self.helpers: List[War3Helper] = []
        self.particle_systems: List[War3ParticleEmitter] = []
        self.particle_systems2: List[War3ParticleSystem] = []
        self.particle_ribbon: List[War3RibbonEmitter] = []
        self.lights: List[War3Light] = []

        self.objects_all: List[War3Node] = []
        self.object_indices: Dict[str, int] = {}
        self.geosets: List[War3Geoset] = []
        self.geoset_map: Dict[Tuple[str, int], War3Geoset] = {}
        self.geoset_anims: List[War3GeosetAnim] = []
        self.geoset_anim_map: Dict[str, War3GeosetAnim] = {}
        self.materials: List[War3Material] = []
        self.sequences: List[War3AnimationAction] = []
        self.global_extents_min: int = 0
        self.global_extents_max: int = 0
        self.const_color_mats = set()
        self.global_seqs: Set[int] = set()
        self.cameras: List = []
        self.textures: List[WarCraft3Texture] = []
        self.tvertex_anims: List[War3TextureAnim] = []

        # self.f2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
        # self.name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")
        self.frame2ms: float = 1000 / 60  # Frame to millisecond conversion
        self.name: str = name

    def register_global_sequence(self, curve: Optional[War3AnimationCurve]):
        if curve is not None and curve.global_sequence > 0:
            self.global_seqs.add(curve.global_sequence)
