from collections import defaultdict

import bpy


class War3Model:

    default_texture = "Textures\white.blp"
    decimal_places = 5

    def __init__(self, context):
        self.objects = defaultdict(set)
        self.objects_all = []
        self.object_indices = {}
        self.geosets = []
        self.geoset_map = {}
        self.geoset_anims = []
        self.geoset_anim_map = {}
        self.materials = []
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
