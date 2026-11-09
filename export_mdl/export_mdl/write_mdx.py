# Binary MDX writer. Writes the same War3Model the MDL writer does, with the layouts HiveWE's mdx_writer.cpp uses.
# Values are written in the order the MDL writer prints them, the one exception being the GeosetAnim static color.
import itertools
import struct
from typing import List, Optional, Dict

from .. import constants
from ..classes.War3AnimationCurve import War3AnimationCurve
from ..classes.War3ExportSettings import War3ExportSettings
from ..classes.War3Layer import War3Layer
from ..classes.War3Model import War3Model
from ..classes.War3Node import War3Node
from ..utils import calc_bounds_radius

NONE = 0xFFFFFFFF

INTERPOLATION = {'DontInterp': 0, 'Linear': 1, 'Hermite': 2, 'Bezier': 3}
LAYER_FILTER_MODES = {name: value for value, name in constants.FILTER_MODES.items()}
EMITTER2_FILTER_MODES = {'None': 0, 'Blend': 0, 'Additive': 1, 'AddAlpha': 1, 'Modulate': 2, 'Modulate2x': 3,
                         'Transparent': 4}
LIGHT_TYPES = {'Omnidirectional': 0, 'Directional': 1, 'Ambient': 2}

# Node flags
BILLBOARDED = 0x8
BILLBOARDED_LOCK_X = 0x10
BILLBOARDED_LOCK_Y = 0x20
BILLBOARDED_LOCK_Z = 0x40
NODE_BONE = 0x100
NODE_LIGHT = 0x200
NODE_EVENT = 0x400
NODE_ATTACHMENT = 0x800
NODE_EMITTER = 0x1000
NODE_COLLISION = 0x2000
NODE_RIBBON = 0x4000
EMITTER_USES_MDL = 0x8000  # Particle emitter 2: Unshaded
EMITTER2_UNSHADED = 0x8000
EMITTER2_SORT_FAR_Z = 0x10000
EMITTER2_LINE_EMITTER = 0x20000
EMITTER2_UNFOGGED = 0x40000
EMITTER2_MODEL_SPACE = 0x80000
EMITTER2_XY_QUAD = 0x100000


class Writer:
    def __init__(self):
        self.buffer = bytearray()

    def pack(self, fmt: str, *values):
        self.buffer += struct.pack('<' + fmt, *values)

    def tag(self, tag: str):
        self.buffer += tag.encode('ascii')

    def string(self, value: str, size: int):
        data = value.encode('utf-8')[:size - 1]
        self.buffer += data + b'\0' * (size - len(data))

    def begin_size(self) -> int:
        position = len(self.buffer)
        self.pack('I', 0)
        return position

    def end_size(self, position: int, inclusive: bool = True):
        size = len(self.buffer) - position - (0 if inclusive else 4)
        struct.pack_into('<I', self.buffer, position, size)


class MdxWriter:
    def __init__(self, model: War3Model, version: int, frame2ms: float, settings: War3ExportSettings):
        self.model = model
        self.version = version
        self.frame2ms = frame2ms
        self.settings = settings
        self.w = Writer()
        self.global_seqs: List[int] = list(model.global_seqs)
        self.bone_ids: Dict[str, int] = {bone.name: bone.obj_id for bone in model.bones}
        # GNDX stores a vertex's matrix group in one byte. Geosets with more groups than that need skin weights,
        # which v900+ has; we switch those to skinning instead of failing.
        # HD shaders read tangents and skin weights too, so their geosets are always skinned.
        self.skinned = set()
        hd_materials = {material.name for material in model.materials if material.layers and material.layers[0].hd}
        for geoset in model.geosets:
            too_many_groups = 256 < len(geoset.matrices)
            if too_many_groups and version < 900:
                raise ValueError("Geoset \"%s\" uses %d bone combinations, version %d allows 256. Export as 900 "
                                 "or newer, or use fewer bone combinations" % (geoset.name, len(geoset.matrices), version))
            hd = geoset.mat_name in hd_materials
            if 900 <= version and (too_many_groups or hd):
                self.skinned.add(id(geoset))
        # Before v1400 a skin weight's bone index (a position in its geoset's bone list) is one byte
        if version < 1400:
            for geoset in model.geosets:
                if id(geoset) in self.skinned:
                    count = len(geoset.skin_matrices(self.bone_ids)[0])
                    if 256 < count:
                        raise ValueError("Geoset %s uses %d bones; version %d skin weights reach 256. Export as "
                                         "1400 or newer" % (geoset.name, count, version))

    def write(self) -> bytes:
        self.w.tag('MDLX')
        self.chunk('VERS', lambda: self.w.pack('I', self.version))
        self.chunk('MODL', self.write_model)
        self.chunk('SEQS', self.write_sequences)
        if self.global_seqs:
            self.chunk('GLBS', lambda: [self.w.pack('I', int(duration)) for duration in self.global_seqs])
        self.optional_chunk('MTLS', self.model.materials, self.write_material)
        self.optional_chunk('TEXS', self.model.textures, self.write_texture)
        self.optional_chunk('TXAN', self.model.tvertex_anims, self.write_texture_animation)
        geosets = [geoset for geoset in self.model.geosets if len(geoset.vertices)]
        self.optional_chunk('GEOS', geosets, self.write_geoset)
        self.optional_chunk('GEOA', self.model.geoset_anims, self.write_geoset_animation)
        self.optional_chunk('BONE', self.model.bones, self.write_bone)
        self.optional_chunk('LITE', self.model.lights, self.write_light)
        self.optional_chunk('HELP', self.model.helpers, self.write_helper)
        attachments = list(enumerate(self.model.attachments))
        self.optional_chunk('ATCH', attachments, self.write_attachment)
        if self.model.objects_all:
            self.chunk('PIVT', lambda: [self.w.pack('3f', *node.pivot) for node in self.model.objects_all])
        self.optional_chunk('PREM', self.model.particle_systems, self.write_emitter)
        self.optional_chunk('PRE2', self.model.particle_systems2, self.write_emitter2)
        self.optional_chunk('RIBB', self.model.particle_ribbon, self.write_ribbon)
        self.optional_chunk('CAMS', self.model.cameras, self.write_camera)
        self.optional_chunk('EVTS', self.model.event_objects, self.write_event_object)
        self.optional_chunk('CLID', self.model.collision_shapes, self.write_collision_shape)
        if self.skinned:
            self.chunk('BPOS', self.write_bind_poses)
        return bytes(self.w.buffer)

    def chunk(self, tag: str, write_body):
        self.w.tag(tag)
        position = self.w.begin_size()
        write_body()
        self.w.end_size(position, inclusive=False)

    def optional_chunk(self, tag: str, items, write_item):
        if items:
            self.chunk(tag, lambda: [write_item(item) for item in items])

    def extent(self, min_extent, max_extent):
        self.w.pack('f3f3f', calc_bounds_radius(min_extent, max_extent), *min_extent, *max_extent)

    def global_seq_id(self, curve: War3AnimationCurve) -> int:
        if curve.global_sequence > 0 and curve.global_sequence in self.global_seqs:
            return self.global_seqs.index(curve.global_sequence)
        return -1

    def track(self, tag: str, curve: Optional[War3AnimationCurve], size: int):
        if curve is None or not curve.keyframes:
            return
        interpolation = INTERPOLATION.get(curve.interpolation, 1)
        tangents = 1 < interpolation
        self.w.tag(tag)
        self.w.pack('IIi', len(curve.keyframes), interpolation, self.global_seq_id(curve))
        for frame in sorted(curve.keyframes):
            self.w.pack('I', int(round(frame * self.frame2ms)))
            self.track_value(curve, curve.keyframes[frame], size)
            if tangents:
                self.track_value(curve, curve.handles_left.get(frame, curve.keyframes[frame]), size)
                self.track_value(curve, curve.handles_right.get(frame, curve.keyframes[frame]), size)

    def track_value(self, curve: War3AnimationCurve, value, size: int):
        value = list(value)
        if curve.type == 'Rotation':
            value = value[1:] + value[:1]  # MDX quaternions are XYZW
        value = (value + [0.0] * size)[:size]
        self.w.pack('%df' % size, *value)

    def node(self, node: War3Node, flags: int, name: Optional[str] = None):
        position = self.w.begin_size()
        self.w.string(node.name if name is None else name, 80)
        if node.billboarded:
            flags |= BILLBOARDED
        flags |= getattr(node, "node_flags", 0) & 0x87
        for locked, flag in zip(node.billboard_lock, (BILLBOARDED_LOCK_Z, BILLBOARDED_LOCK_Y, BILLBOARDED_LOCK_X)):
            if locked:
                flags |= flag
        self.w.pack('IIi', node.obj_id, NONE if node.parent_id is None else node.parent_id, flags)
        self.track('KGTR', node.anim_loc, 3)
        self.track('KGRT', node.anim_rot, 4)
        self.track('KGSC', node.anim_scale, 3)
        self.w.end_size(position)

    def write_model(self):
        self.w.string(self.model.name, 80)
        self.w.string('', 260)
        self.extent(self.model.global_extents_min, self.model.global_extents_max)
        self.w.pack('I', 150)

    def write_sequences(self):
        for sequence in self.model.sequences:
            self.w.string(sequence.name, 80)
            self.w.pack('II', int(round(sequence.start * self.frame2ms)), int(round(sequence.end * self.frame2ms)))
            move_speed = sequence_move_speed(sequence)
            self.w.pack('fIfI', move_speed, 1 if sequence.non_looping else 0, max(sequence.rarity, 0), 0)
            self.extent(self.model.global_extents_min, self.model.global_extents_max)

    def write_texture(self, texture):
        replaceable = texture.texture_path.startswith("ReplaceableId")
        self.w.pack('I', int(texture.replaceable_id) if replaceable else 0)
        self.w.string('' if replaceable else texture.texture_path, 260)
        self.w.pack('I', 3)  # WrapWidth | WrapHeight, like the MDL writer

    def write_texture_animation(self, texture_anim):
        position = self.w.begin_size()
        self.track('KTAT', texture_anim.translation, 3)
        self.track('KTAR', texture_anim.rotation, 4)
        self.track('KTAS', texture_anim.scale, 3)
        self.w.end_size(position)

    def write_material(self, material):
        position = self.w.begin_size()
        self.w.pack('iI', material.priority_plane, 0x1 if material.use_const_color else 0)
        hd = 900 <= self.version and material.layers[0].hd
        shader_id = (material.layers[0].shader or 1) if hd else 0
        if self.version in (900, 1000):
            self.w.string(constants.SHADER_NAMES[shader_id] if hd else '', 80)
        self.w.tag('LAYS')
        if hd and 1100 <= self.version:
            # One layer that binds every PBR texture to its slot
            self.w.pack('I', 1)
            self.write_layer(material.layers[0], material.layers, shader_id)
        elif hd:
            # v900/v1000 spread an HD material over one layer per texture, only the first one has tracks
            self.w.pack('I', len(material.layers))
            for i, layer in enumerate(material.layers):
                self.write_layer(material.layers[0], [layer], shader_id, tracks=i == 0)
        else:
            self.w.pack('I', len(material.layers))
            for layer in material.layers:
                self.write_layer(layer, [layer], 0)
        self.w.end_size(position)

    def write_layer(self, layer: War3Layer, texture_layers: List[War3Layer], shader_id: int, tracks: bool = True):
        position = self.w.begin_size()
        flags = 0
        for flag, enabled in ((0x1, layer.unshaded), (0x2, layer.sphere_env_map), (0x4, layer.wrap_width),
                              (0x8, layer.wrap_height), (0x10, layer.two_sided), (0x20, layer.unfogged),
                              (0x40, layer.no_depth_test), (0x80, layer.no_depth_set), (0x100, layer.unlit),
                              (0x200, layer.back_faces_for_shadows), (0x400, layer.ambient_occlusion)):
            if enabled:
                flags |= flag
        texture_ids = [self.texture_id(texture_layer) for texture_layer in texture_layers]
        texture_anim = NONE if layer.texture_anim is None else self.model.tvertex_anims.index(layer.texture_anim)
        self.w.pack('III', LAYER_FILTER_MODES.get(layer.filter_mode, 0), flags, texture_ids[0])
        self.w.pack('IIf', texture_anim, 0, layer.alpha_value)
        if 800 < self.version:
            self.w.pack('f', layer.emissive_gain)
        if 900 < self.version:
            self.w.pack('3fff', *layer.fresnel_color, layer.fresnel_opacity, layer.fresnel_team_color)
        if 1000 < self.version:
            self.w.pack('II', shader_id, len(texture_ids))
            for slot, texture_id in enumerate(texture_ids):
                self.w.pack('II', texture_id, slot)
        if tracks:
            self.track('KMTA', layer.alpha_anim, 1)
            if 800 < self.version:
                self.track('KMTE', layer.emissive_gain_anim, 1)
            if 900 < self.version:
                self.track('KFC3', layer.fresnel_color_anim, 3)
                self.track('KFCA', layer.fresnel_opacity_anim, 1)
                self.track('KFTC', layer.fresnel_team_color_anim, 1)
        self.w.end_size(position)

    def texture_id(self, layer: War3Layer) -> int:
        if layer.texture is not None and layer.texture in self.model.textures:
            return self.model.textures.index(layer.texture)
        return 0

    def write_geoset(self, geoset):
        position = self.w.begin_size()
        vertices = geoset.vertices
        skin = id(geoset) in self.skinned
        self.w.tag('VRTX')
        self.w.pack('I', len(vertices))
        for vertex in vertices:
            self.w.pack('3f', *vertex.pos)
        self.w.tag('NRMS')
        self.w.pack('I', len(vertices))
        for vertex in vertices:
            self.w.pack('3f', *vertex.normal)
        indices = list(itertools.chain.from_iterable(geoset.triangles))
        self.w.tag('PTYP')
        self.w.pack('II', 1, 4)  # Triangles
        self.w.tag('PCNT')
        self.w.pack('II', 1, len(indices))
        self.w.tag('PVTX')
        self.w.pack('I%dH' % len(indices), len(indices), *indices)

        if skin:
            # Skinned geosets leave the vertex groups empty; the matrix list holds one group per bone they use, and
            # the skin's bone indices are positions in it
            skin_ids, skins = geoset.skin_matrices(self.bone_ids)
            groups, matrices = [], [[node_id] for node_id in skin_ids]
        else:
            groups = [geoset.matrices.index(vertex.bone_list) if vertex.bone_list in geoset.matrices else 0
                      for vertex in vertices]
            matrices = [[self.bone_ids.get(name, 0) for name in matrix] for matrix in geoset.matrices]
        self.w.tag('GNDX')
        self.w.pack('I%dB' % len(groups), len(groups), *groups)
        self.w.tag('MTGC')
        self.w.pack('I%dI' % len(matrices), len(matrices), *(len(matrix) for matrix in matrices))
        matrix_indices = list(itertools.chain.from_iterable(matrices))
        self.w.tag('MATS')
        self.w.pack('I%dI' % len(matrix_indices), len(matrix_indices), *matrix_indices)

        material_names = [material.name for material in self.model.materials]
        self.w.pack('III', material_names.index(geoset.mat_name), 0, 0)
        if 800 < self.version:
            self.w.pack('I', 0)
            self.w.string('', 80)
        self.extent(geoset.min_extent, geoset.max_extent)
        self.w.pack('I', len(self.model.sequences))
        for _ in self.model.sequences:
            self.extent(geoset.min_extent, geoset.max_extent)

        if skin:
            self.w.tag('TANG')
            self.w.pack('I', len(vertices))
            for vertex in vertices:
                self.w.pack('4f', *vertex.tangent)
            self.w.tag('SKIN')
            self.w.pack('I', len(vertices) * 8)
            skin_format = '8H' if 1400 <= self.version else '8B'
            for vertex, bones in zip(vertices, skins):
                weights = (list(vertex.weight_list) + [0, 0, 0, 0])[:4]
                if skin_format == '8B' and 255 < max(bones):
                    raise ValueError("A geoset uses %d bones; more than 256 need format version 1400 or newer"
                                     % len(skin_ids))
                self.w.pack(skin_format, *bones, *(int(weight) for weight in weights))

        self.w.tag('UVAS')
        self.w.pack('I', 1)
        self.w.tag('UVBS')
        self.w.pack('I', len(vertices))
        for vertex in vertices:
            self.w.pack('2f', *vertex.uv)
        self.w.end_size(position)

    def write_geoset_animation(self, geoset_anim):
        position = self.w.begin_size()
        alpha = geoset_anim.alpha[0] if geoset_anim.alpha else 1.0
        color = list(geoset_anim.color[:3]) if geoset_anim.color is not None else [1.0, 1.0, 1.0]
        has_color = geoset_anim.uses_color()
        # MDX stores every color RGB (checked on Blizzard's fire particles, ice torch tint, lights, ribbons);
        # only MDL text writes them BGR
        self.w.pack('fI3fI', alpha, 0x2 if has_color else 0, *color, geoset_anim.geoset_id)
        self.track('KGAO', geoset_anim.alpha_anim, 1)
        self.track('KGAC', geoset_anim.color_anim, 3)
        self.w.end_size(position)

    def write_bone(self, bone):
        self.node(bone, NODE_BONE, bone.name.replace('.', '_'))
        children = [g for g in self.model.geosets if bone.name in itertools.chain.from_iterable(g.matrices)]
        geoset_id = self.model.geosets.index(children[0]) if len(children) == 1 else -1
        geoset_anim = self.model.geoset_anim_map.get(bone.name)
        geoset_anim_id = self.model.geoset_anims.index(geoset_anim) if geoset_anim is not None else -1
        self.w.pack('ii', geoset_id, geoset_anim_id)

    def write_helper(self, helper):
        self.node(helper, 0, helper.name.replace('.', '_'))

    def write_light(self, light):
        position = self.w.begin_size()
        self.node(light, NODE_LIGHT)
        self.w.pack('I', LIGHT_TYPES.get(light.light_type, 0))
        if 1300 <= self.version:
            self.w.pack('I', 1 if light.shadow_casting else 0)
        self.w.pack('ff3ff3ff', light.atten_start, light.atten_end, *light.color[:3], light.intensity,
                    *light.amb_color[:3], light.amb_intensity)
        if 1200 <= self.version:
            self.w.pack('f', 0.4 if light.shadow_intensity is None else light.shadow_intensity)
        if 1300 <= self.version:
            self.w.pack('ff', light.shadow_casting_start, light.shadow_casting_end)
        if 1600 <= self.version:
            self.w.pack('fff', light.quadratic_falloff, light.linear_falloff, light.damping)
        self.track('KLAS', light.atten_start_anim, 1)
        self.track('KLAE', light.atten_end_anim, 1)
        self.track('KLAC', light.color_anim, 3)
        self.track('KLAI', light.intensity_anim, 1)
        self.track('KLBI', light.amb_intensity_anim, 1)
        self.track('KLBC', light.amb_color_anim, 3)
        self.track('KLAV', light.visibility, 1)
        if 1300 <= self.version:
            self.track('KLSS', light.shadow_casting_start_anim, 1)
            self.track('KLSE', light.shadow_casting_end_anim, 1)
        if 1600 <= self.version:
            self.track('KLQF', light.quadratic_falloff_anim, 1)
            self.track('KLLF', light.linear_falloff_anim, 1)
            self.track('KLDA', light.damping_anim, 1)
        self.w.end_size(position)

    def write_attachment(self, indexed_attachment):
        attachment_id, attachment = indexed_attachment
        position = self.w.begin_size()
        self.node(attachment, NODE_ATTACHMENT)
        self.w.string(getattr(attachment, 'path', '') or '', 256)
        self.w.pack('II', 0, attachment_id)
        self.track('KATV', attachment.visibility, 1)
        self.w.end_size(position)

    def write_emitter(self, psys):
        emitter = psys.emitter
        position = self.w.begin_size()
        self.node(psys, NODE_EMITTER | EMITTER_USES_MDL)
        self.w.pack('ffff', emitter.emission_rate, emitter.gravity, emitter.longitude, emitter.latitude)
        self.w.string(emitter.model_path, 260)
        self.w.pack('ff', emitter.life_span, emitter.speed)
        self.track('KPEE', psys.emission_rate_anim, 1)
        self.track('KPEG', psys.gravity_anim, 1)
        self.track('KPLN', psys.longitude_anim, 1)
        self.track('KPLT', psys.latitude_anim, 1)
        self.track('KPEL', psys.life_span_anim, 1)
        self.track('KPES', psys.speed_anim, 1)
        self.track('KPEV', psys.visibility, 1)
        self.w.end_size(position)

    def write_emitter2(self, psys):
        emitter = psys.emitter
        position = self.w.begin_size()
        flags = NODE_EMITTER
        for flag, enabled in ((EMITTER2_UNSHADED, emitter.unshaded), (EMITTER2_SORT_FAR_Z, emitter.sort_far_z),
                              (EMITTER2_LINE_EMITTER, emitter.line_emitter), (EMITTER2_UNFOGGED, emitter.unfogged),
                              (EMITTER2_MODEL_SPACE, emitter.model_space), (EMITTER2_XY_QUAD, emitter.xy_quad)):
            if enabled:
                flags |= flag
        self.node(psys, flags)
        self.w.pack('ffffff', emitter.speed, emitter.variation, emitter.latitude, emitter.gravity,
                    emitter.life_span, emitter.emission_rate)
        self.w.pack('ff', psys.dimensions[0], psys.dimensions[1])  # Length, width
        head_or_tail = 2 if emitter.head and emitter.tail else 1 if emitter.tail else 0
        self.w.pack('IIIIff', EMITTER2_FILTER_MODES.get(emitter.filter_mode, 0), emitter.rows, emitter.cols,
                    head_or_tail, emitter.tail_length, emitter.time)
        for color in (emitter.start_color, emitter.mid_color, emitter.end_color):
            self.w.pack('3f', *color[:3])
        self.w.pack('3B', emitter.start_alpha, emitter.mid_alpha, emitter.end_alpha)
        self.w.pack('3f', emitter.start_scale, emitter.mid_scale, emitter.end_scale)
        self.w.pack('3I', emitter.head_life_start, emitter.head_life_end, emitter.head_life_repeat)
        self.w.pack('3I', emitter.head_decay_start, emitter.head_decay_end, emitter.head_decay_repeat)
        self.w.pack('3I', emitter.tail_life_start, emitter.tail_life_end, emitter.tail_life_repeat)
        self.w.pack('3I', emitter.tail_decay_start, emitter.tail_decay_end, emitter.tail_decay_repeat)
        texture_id = self.model.textures.index(psys.texture) if psys.texture in self.model.textures else 0
        self.w.pack('IIiI', texture_id, 0, emitter.priority_plane, 0)  # Squirt and replaceable id unused
        self.track('KP2S', psys.speed_anim, 1)
        self.track('KP2R', psys.variation_anim, 1)
        self.track('KP2L', psys.latitude_anim, 1)
        self.track('KP2G', psys.gravity_anim, 1)
        self.track('KP2E', psys.emission_rate_anim, 1)
        self.track('KP2V', psys.visibility, 1)
        self.w.end_size(position)

    def write_ribbon(self, psys):
        emitter = psys.emitter
        position = self.w.begin_size()
        self.node(psys, NODE_RIBBON)
        material_names = [material.name for material in self.model.materials]
        ribbon_material = emitter.ribbon_material
        material_id = material_names.index(ribbon_material.name) \
            if ribbon_material is not None and ribbon_material.name in material_names else 0
        self.w.pack('fff3ff', psys.dimensions[0] / 2, psys.dimensions[0] / 2, emitter.alpha,
                    *emitter.ribbon_color[:3], emitter.life_span)
        self.w.pack('IIIIIf', 0, int(emitter.emission_rate), emitter.rows, emitter.cols, material_id, emitter.gravity)
        self.track('KRAL', psys.alpha_anim, 1)
        self.track('KRCO', psys.ribbon_color_anim, 3)
        self.track('KRVS', psys.visibility, 1)
        self.w.end_size(position)

    def write_camera(self, camera):
        position = self.w.begin_size()
        self.w.string(camera.name, 80)
        self.w.pack('3ffff3f', *camera.pivot, camera.field_of_view, camera.far_clip, camera.near_clip, *camera.target)
        self.w.end_size(position)

    def write_event_object(self, event):
        self.node(event, NODE_EVENT)
        track = event.track
        times = [] if track is None else [int(round(frame * self.frame2ms)) for frame in sorted(track.keyframes)]
        self.w.tag('KEVT')
        self.w.pack('Ii', len(times), -1 if track is None else self.global_seq_id(track))
        self.w.pack('%dI' % len(times), *times)

    def write_collision_shape(self, collider):
        self.node(collider, NODE_COLLISION)
        if collider.type == 'Box':
            self.w.pack('I', 0)
            for vert in collider.verts[:2]:
                self.w.pack('3f', *vert)
        else:
            self.w.pack('I3ff', 2, *collider.verts[0], collider.radius)

    def write_bind_poses(self):
        nodes = list(self.model.objects_all) + list(self.model.cameras)
        self.w.pack('I', len(nodes))
        for node in nodes:
            self.w.pack('12f', *bind_pose(node))


def sequence_move_speed(sequence) -> float:
    """Walk sequences always carry it; others only when set to something other than the untouched default (270),
    as Blizzard's do on some Stand sequences."""
    speed = sequence.movement_speed or 0
    if 'walk' in sequence.name.lower() or speed != 270:
        return float(speed)
    return 0.0


def bind_pose(node) -> List[float]:
    """A node's rest matrix as BPOS stores it: three axis columns, then the translation, which Blizzard's
    models always set to the node's pivot (a camera's position). The axes hold Maya joint orientations in
    Blizzard's files, which Blender bones don't have, so they're written as identity."""
    pivot = list(node.pivot)[:3] if getattr(node, 'pivot', None) is not None else [0.0, 0.0, 0.0]
    return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [float(v) for v in pivot]


def write_mdx_file(filepath: str, version: int, model: War3Model, frame2ms: float, settings: War3ExportSettings):
    data = MdxWriter(model, version, frame2ms, settings).write()
    with open(filepath, 'wb') as output:
        output.write(data)
