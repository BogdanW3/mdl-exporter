from typing import List

from mathutils import Vector

from export_mdl.alt_classes.Bone import Bone
from export_mdl.alt_classes.Geoset import Geoset
from export_mdl.alt_classes.GeosetAnim import GeosetAnim
from export_mdl.alt_classes.Material import Material
from export_mdl.alt_classes.Node import Node
from export_mdl.alt_classes.Sequence import Sequence
from export_mdl.alt_classes.TextureAnimaton import TextureAnimation


class WC3Model:
    def __init__(self):
        self.sequences: List[Sequence] = []
        self.global_seqs: List[float] = []
        self.textures: List[str] = []
        self.materials: List[Material] = []
        self.texture_anims: List[TextureAnimation] = []
        self.geosets: List[Geoset] = []
        self.geoset_anims: List[GeosetAnim] = []
        self.bones: List[Bone] = []
        self.lights: List[Node] = []
        self.helpers: List[Node] = []
        self.attachments: List[Node] = []
        self.pivot_points: List[Vector] = []
        self.particle_emitters: List[Node] = []
        self.particle_emitters2: List[Node] = []
        self.ribbon_emitters: List[Node] = []
        self.cameras: List[Node] = []
        self.event_objects: List[Node] = []
        self.collisionShapes: List[Node] = []

