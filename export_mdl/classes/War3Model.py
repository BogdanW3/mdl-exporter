import itertools
import math
from collections import defaultdict
from operator import itemgetter

import bmesh
import bpy
from mathutils import Vector

from .War3Material import War3Material
from .War3MaterialLayer import War3MaterialLayer
from .War3Geoset import War3Geoset
from .War3GeosetAnim import War3GeosetAnim
from .War3AnimationCurve import War3AnimationCurve
from .War3ParticleSystem import War3ParticleSystem
from .War3Object import War3Object
from .model_utils.get_sequences import get_sequences
from .model_utils.get_visibility import get_visibility
from .model_utils.register_global_sequence import register_global_sequence
from .utils.transform_rot import transform_rot
from .utils.transform_vec import transform_vec
from ..utils import get_curves, calc_extents, rnd


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

        self.f2ms = 1000 / context.scene.render.fps  # Frame to milisecond conversion
        self.name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")

    @staticmethod
    def prepare_mesh(obj, context, matrix):
        mod = None
        if obj.data.use_auto_smooth:
            mod = obj.modifiers.new("EdgeSplitExport", 'EDGE_SPLIT')
            mod.split_angle = obj.data.auto_smooth_angle
            # mod.use_edge_angle = True

        depsgraph = context.evaluated_depsgraph_get()
        mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)

        if obj.data.use_auto_smooth:
            obj.modifiers.remove(mod)

        # Triangulate for web export
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # If an object has had a negative scale applied, normals will be inverted. This will fix that.
        if any(s < 0 for s in obj.scale):
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        del bm

        mesh.calc_normals_split()
        mesh.calc_loop_triangles()

        return mesh

    @staticmethod
    def get_parent(obj):
        parent = obj.parent

        if parent is None:
            return None # Instead return object name??

        if obj.parent_type == 'BONE':  # TODO: Check if animated - otherwise, make it a helper
            return obj.parent_bone if obj.parent_bone != "" else None

        if parent.type == 'EMPTY' and parent.name.startswith("Bone_"):
            return parent.name

        anim_loc = get_curves(parent, 'location', (1, 2, 3))
        anim_rot = get_curves(parent, 'rotation_quaternion', (1, 2, 3, 4))
        anim_scale = get_curves(parent, 'scale', (1, 2, 3))
        animations = (anim_loc, anim_rot, anim_scale)

        if not any(animations):
            root_parent = War3Model.get_parent(parent)
            if root_parent is not None:
                return root_parent

        return parent.name

    def from_scene(self, context, settings):

        scene = context.scene

        self.sequences = get_sequences(self.f2ms, scene)

        objs = []
        mats = set()

        if settings.use_selection:
            objs = (obj for obj in scene.objects if obj.select_get() and obj.visible_get())
        else:
            objs = (obj for obj in scene.objects if obj.visible_get())

        for obj in objs:
            parent = War3Model.get_parent(obj)

            billboarded = False
            billboard_lock = (False, False, False)
            if hasattr(obj, "mdl_billboard"):
                bb = obj.mdl_billboard
                billboarded = bb.billboarded
                billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
                # NOTE: Axes are listed backwards (same as with colors)

            # Animations
            visibility = get_visibility(self.sequences, obj)

            # Particle Systems
            if len(obj.particle_systems):
                self.add_particle_systems(billboard_lock, billboarded, mats, obj, parent, settings)

            # Collision Shapes
            elif obj.type == 'EMPTY' and obj.name.startswith('Collision'):
                self.create_collision_shapes(obj, parent, settings)

            elif obj.type == 'MESH' or obj.type == 'CURVE':
                self.make_mesh(billboard_lock, billboarded, context, mats, obj, parent, settings)

            elif obj.type == 'EMPTY':
                self.add_empties_animations(billboard_lock, billboarded, obj, parent, settings)

            elif obj.type == 'ARMATURE':
                self.add_bones(billboard_lock, billboarded, obj, parent, settings)

            elif obj.type in ('LAMP', 'LIGHT'):
                self.add_lights(billboard_lock, billboarded, obj, settings)

            elif obj.type == 'CAMERA':
                self.cameras.append(obj)


        self.geosets = list(self.geoset_map.values())
        self.materials = [War3Material.get(mat, self) for mat in mats]

        # Add default material if no other materials present
        if any((x for x in self.geosets if x.mat_name == "default")):
            default_mat = War3Material("default")
            default_mat.layers.append(War3MaterialLayer())
            self.materials.append(default_mat)

        self.materials = sorted(self.materials, key=lambda x: x.priority_plane)

        layers = list(itertools.chain.from_iterable([material.layers for material in self.materials]))
        self.textures = list(set((layer.texture for layer in layers)))
        # Convert to set and back to list for unique entries

        # Demote bones to helpers if they have no attached geosets
        for bone in self.objects['bone']:
            if not any([g for g in self.geosets if bone.name in itertools.chain.from_iterable(g.matrices)]):
                self.objects['helper'].add(bone)

        self.objects['bone'] -= self.objects['helper']
        # We also need the textures used by emitters
        for psys in list(self.objects['particle']) + list(self.objects['particle2']) + list(self.objects['ribbon']):
            if psys.emitter.texture_path not in self.textures:
                self.textures.append(psys.emitter.texture_path)

        self.tvertex_anims = list(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))

        vertices_all = []

        self.objects_all = []
        self.object_indices = {}

        index = 0
        for tag in ('bone', 'light', 'helper', 'attachment', 'particle', 'particle2', 'ribbon', 'eventobject', 'collisionshape'):
            for object in self.objects[tag]:
                self.object_indices[object.name] = index
                self.objects_all.append(object)
                vertices_all.append(object.pivot)
                if tag == 'collisionshape':
                    for vert in object.verts:
                        vertices_all.append(vert)
                index = index+1

        for geoset in self.geosets:
            for vertex in geoset.vertices:
                vertices_all.append(vertex[0])

            geoset.min_extent, geoset.max_extent = calc_extents([x[0] for x in geoset.vertices])

            if geoset.geoset_anim is not None:
                register_global_sequence(self.global_seqs, geoset.geoset_anim.alpha_anim)
                register_global_sequence(self.global_seqs, geoset.geoset_anim.color_anim)

                for bone in itertools.chain.from_iterable(geoset.matrices):
                    self.geoset_anim_map[bone] = geoset.geoset_anim

        # Account for particle systems when calculating bounds
        for psys in list(self.objects['particle']) + list(self.objects['particle2']) + list(self.objects['ribbon']):
            vertices_all.append(tuple(x + y/2 for x, y in zip(psys.pivot, psys.dimensions)))
            vertices_all.append(tuple(x - y/2 for x, y in zip(psys.pivot, psys.dimensions)))

        self.geoset_anims = list(set(g.geoset_anim for g in self.geosets if g.geoset_anim is not None))

        self.global_extents_min, self.global_extents_max = calc_extents(vertices_all) if len(vertices_all) else ((0, 0, 0), (0, 0, 0))
        self.global_seqs = sorted(self.global_seqs)

    def add_particle_systems(self, billboard_lock, billboarded, mats, obj, parent, settings):
        visibility = get_visibility(self.sequences, obj)
        anim_loc, anim_rot, anim_scale, is_animated = self.is_animated_ugg(obj, settings)
        data = obj.particle_systems[0].settings

        if getattr(data, "mdl_particle_sys"):
            particle_sys = War3ParticleSystem(obj.name, obj, self)

            particle_sys.pivot = settings.global_matrix @ Vector(obj.location)

            # particle_sys.dimensions = obj.matrix_world.to_quaternion() * Vector(obj.scale)
            particle_sys.dimensions = Vector(map(abs, settings.global_matrix @ obj.dimensions))

            particle_sys.parent = parent
            particle_sys.visibility = visibility
            register_global_sequence(self.global_seqs, particle_sys.visibility)

            if is_animated:
                bone = self.create_bone(anim_loc, anim_rot, anim_scale, obj, parent, settings)
                register_global_sequence(self.global_seqs, bone.anim_loc)
                register_global_sequence(self.global_seqs, bone.anim_rot)
                register_global_sequence(self.global_seqs, bone.anim_scale)

                if bone.anim_loc is not None:
                    transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation,
                                  bone.anim_loc.handles_right, bone.anim_loc.handles_left,
                                  settings.global_matrix)

                if bone.anim_rot is not None:
                    transform_rot(bone.anim_rot.keyframes, settings.global_matrix)

                bone.billboarded = billboarded
                bone.billboard_lock = billboard_lock
                self.objects['bone'].add(bone)
                particle_sys.parent = bone.name

            if particle_sys.emitter.emitter_type == 'ParticleEmitter':
                self.objects['particle'].add(particle_sys)

            elif particle_sys.emitter.emitter_type == 'ParticleEmitter2':
                self.objects['particle2'].add(particle_sys)

            else:
                # Add the material to the list, in case it's unused
                mat = particle_sys.emitter.ribbon_material
                mats.add(mat)

                self.objects['ribbon'].add(particle_sys)

    def create_bone(self, anim_loc, anim_rot, anim_scale, obj, parent, settings):
        bone = War3Object(obj.name)
        if parent is not None:
            bone.parent = parent
        else:
            bone.parent = parent

        bone.pivot = settings.global_matrix @ Vector(obj.location)
        bone.anim_loc = anim_loc
        bone.anim_rot = anim_rot
        bone.anim_scale = anim_scale
        return bone

    def is_animated_ugg(self, obj, settings):
        anim_loc = War3AnimationCurve.get(obj.animation_data, 'location', 3, self.sequences)
        # get_curves(obj, 'location', (0, 1, 2))

        if anim_loc is not None and settings.optimize_animation:
            anim_loc.optimize(settings.optimize_tolerance, self.sequences)

        anim_rot = War3AnimationCurve.get(obj.animation_data, 'rotation_quaternion', 4, self.sequences)
        # get_curves(obj, 'rotation_quaternion', (0, 1, 2, 3))

        if anim_rot is None:
            anim_rot = War3AnimationCurve.get(obj.animation_data, 'rotation_euler', 3, self.sequences)

        if anim_rot is not None and settings.optimize_animation:
            anim_rot.optimize(settings.optimize_tolerance, self.sequences)

        anim_scale = War3AnimationCurve.get(obj.animation_data, 'scale', 3, self.sequences)
        # get_curves(obj, 'scale', (0, 1, 2))

        if anim_scale is not None and settings.optimize_animation:
            anim_scale.optimize(settings.optimize_tolerance, self.sequences)

        is_animated = any((anim_loc, anim_rot, anim_scale))
        return anim_loc, anim_rot, anim_scale, is_animated

    def make_mesh(self, billboard_lock, billboarded, context, mats, obj, parent, settings):
        visibility = get_visibility(self.sequences, obj)
        anim_loc, anim_rot, anim_scale, is_animated = self.is_animated_ugg(obj, settings)
        mesh = self.prepare_mesh(obj, context, settings.global_matrix @ obj.matrix_world)

        # Geoset Animation
        vertex_color_anim = War3AnimationCurve.get(obj.animation_data, 'color', 3, self.sequences)
        vertex_color = None

        if any(i < 0.999 for i in obj.color[:3]):
            vertex_color = tuple(obj.color[:3])

        if not any((vertex_color, vertex_color_anim)):
            mat = obj.active_material
            if mat is not None and hasattr(mat, "node_tree") and mat.node_tree is not None:
                node = mat.node_tree.nodes.get("VertexColor")
                if node is not None:
                    attr = "outputs" if node.bl_idname == 'ShaderNodeRGB' else "inputs"
                    vertex_color = tuple(getattr(node, attr)[0].default_value[:3])
                    if hasattr(mat.node_tree, "animation_data"):
                        vertex_color_anim = War3AnimationCurve.get(
                            mat.node_tree.animation_data, 'nodes["VertexColor"].%s[0].default_value' % attr, 3, self.sequences)
        geoset_anim = None
        geoset_anim_hash = 0
        if any((vertex_color, vertex_color_anim, visibility)):
            geoset_anim = War3GeosetAnim(vertex_color, vertex_color_anim, visibility)
            geoset_anim_hash = hash(geoset_anim)  # The hash is a bit complex, so we precompute it

        mesh_geosets = set()
        armature = None

        for m in obj.modifiers:
            if m.type == 'ARMATURE':
                armature = m

        bone_names = set()

        if armature is not None:
            bone_names = set(b.name for b in armature.object.data.bones)

        bone = None
        if (armature is None and parent is None) or is_animated:
            bone = self.create_bone(anim_loc, anim_rot, anim_scale, obj, parent, settings)
            # bone = War3Object(obj.name)  # Object is animated or parent is missing - create a bone for it!
            #
            # bone.parent = parent  # Remember to make it the parent - parent is added to matrices further down
            # bone.pivot = settings.global_matrix @ Vector(obj.location)
            # bone.anim_loc = anim_loc
            # bone.anim_rot = anim_rot
            # bone.anim_scale = anim_scale

            if bone.anim_loc is not None:
                register_global_sequence(self.global_seqs, bone.anim_loc)
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                              bone.anim_loc.handles_left, obj.matrix_world.inverted())
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                              bone.anim_loc.handles_left, settings.global_matrix)

            if bone.anim_rot is not None:
                register_global_sequence(self.global_seqs, bone.anim_rot)
                transform_rot(bone.anim_rot.keyframes, obj.matrix_world.inverted())
                transform_rot(bone.anim_rot.keyframes, settings.global_matrix)

            register_global_sequence(self.global_seqs, bone.anim_scale)
            bone.billboarded = billboarded
            bone.billboard_lock = billboard_lock

            if geoset_anim is not None:
                self.geoset_anim_map[bone] = geoset_anim
            self.objects['bone'].add(bone)
            parent = bone.name

        for tri in mesh.loop_triangles:
            # p = mesh.polygons[f.index]
            # Textures and materials
            mat_name = "default"
            if obj.material_slots and len(obj.material_slots):
                mat = obj.material_slots[tri.material_index].material
                if mat is not None:
                    mat_name = mat.name
                    mats.add(mat)

            geoset = None
            if (mat_name, geoset_anim_hash) in self.geoset_map.keys():
                geoset = self.geoset_map[(mat_name, geoset_anim_hash)]
            else:
                geoset = War3Geoset()
                geoset.mat_name = mat_name
                if geoset_anim is not None:
                    geoset.geoset_anim = geoset_anim
                    geoset_anim.geoset = geoset

                self.geoset_map[(mat_name, geoset_anim_hash)] = geoset

            # Vertices, faces, and matrices
            vertex_map = {}
            for vert, loop in zip(tri.vertices, tri.loops):
                co = mesh.vertices[vert].co
                coord = (rnd(co.x), rnd(co.y), rnd(co.z))
                n = mesh.vertices[vert].normal if tri.use_smooth else tri.normal
                norm = (rnd(n.x), rnd(n.y), rnd(n.z))
                uv = mesh.uv_layers.active.data[loop].uv if len(mesh.uv_layers) else Vector((0.0, 0.0))
                uv[1] = 1 - uv[1]  # For some reason, uv Y coordinates appear flipped. This should fix that.
                tvert = (rnd(uv.x), rnd(uv.y))
                groups = None
                matrix = 0

                if armature is not None:
                    vertex_groups = sorted(mesh.vertices[vert].groups[:], key=lambda x: x.weight,
                                     reverse=True)  # Sort bones by descending weight
                    if len(vertex_groups):
                        # Warcraft does not support vertex weights, so we exclude groups with too small influence
                        groups = list(obj.vertex_groups[vg.group].name for vg in vertex_groups if
                                      (obj.vertex_groups[vg.group].name in bone_names and vg.weight > 0.25))[:3]
                        if not len(groups):
                            for vg in vertex_groups:
                                # If we didn't find a group, just take the best match (the list is already sorted by weight)
                                if obj.vertex_groups[vg.group].name in bone_names:
                                    groups = [obj.vertex_groups[vg.group].name]
                                    break

                if parent is not None and (groups is None or len(groups) == 0):
                    groups = [parent]

                if groups is not None:
                    if groups not in geoset.matrices:
                        geoset.matrices.append(groups)
                    matrix = geoset.matrices.index(groups)

                vertex = (coord, norm, tvert, matrix)
                if vertex not in geoset.vertices:
                    geoset.vertices.append(vertex)

                vertex_map[vert] = geoset.vertices.index(vertex)

            # Triangles, normals, vertices, and UVs
            geoset.triangles.append(
                (vertex_map[tri.vertices[0]], vertex_map[tri.vertices[1]], vertex_map[tri.vertices[2]]))

            mesh_geosets.add(geoset)
        for geoset in mesh_geosets:
            geoset.objects.append(obj)
            if not len(geoset.matrices) and parent is not None:
                geoset.matrices.append([parent])

        # obj.to_mesh_clear()
        bpy.data.meshes.remove(mesh)

    def add_empties_animations(self, billboard_lock, billboarded, obj, parent, settings):
        visibility = get_visibility(self.sequences, obj)
        anim_loc, anim_rot, anim_scale, is_animated = self.is_animated_ugg(obj, settings)
        if obj.name.startswith("SND") or obj.name.startswith("UBR") or obj.name.startswith(
                "FTP") or obj.name.startswith("SPL"):
            eventobj = War3Object(obj.name)
            eventobj.pivot = settings.global_matrix @ Vector(obj.location)

            for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
                eventobj.track = War3AnimationCurve.get(obj.animation_data, datapath, 1, self.sequences)
                # get_curve(obj, ['["eventtrack"]', '["EventTrack"]', '["event_track"]'])

                if eventobj.track is not None:
                    register_global_sequence(self.global_seqs, eventobj.track)
                    break

            self.objects['eventobject'].add(eventobj)

        elif obj.name.endswith(" Ref"):
            att = War3Object(obj.name)
            att.pivot = settings.global_matrix @ Vector(obj.location)
            att.parent = parent
            att.visibility = visibility
            register_global_sequence(self.global_seqs, visibility)
            att.billboarded = billboarded
            att.billboard_lock = billboard_lock
            self.objects['attachment'].add(att)

        elif obj.name.startswith("Bone_"):
            bone = self.create_bone(anim_loc, anim_rot, anim_scale, obj, parent, settings)
            # bone = War3Object(obj.name)
            # if parent is not None:
            #     bone.parent = parent
            # bone.pivot = settings.global_matrix @ Vector(obj.location)
            # bone.anim_loc = anim_loc
            # bone.anim_scale = anim_scale
            # bone.anim_rot = anim_rot

            register_global_sequence(self.global_seqs, bone.anim_scale)

            if bone.anim_loc is not None:
                register_global_sequence(self.global_seqs, bone.anim_loc)
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                              bone.anim_loc.handles_left, obj.matrix_world.inverted())
                # if obj.parent is not None:
                #     bone.anim_loc.transform_vec(obj.parent.matrix_world.inverted())
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                              bone.anim_loc.handles_left, settings.global_matrix)

            if bone.anim_rot is not None:
                register_global_sequence(self.global_seqs, bone.anim_rot)
                transform_rot(bone.anim_rot.keyframes, obj.matrix_world.inverted())
                transform_rot(bone.anim_rot.keyframes, settings.global_matrix)

            bone.billboarded = billboarded
            bone.billboard_lock = billboard_lock
            self.objects['bone'].add(bone)

    def add_bones(self, billboard_lock, billboarded, obj, parent, settings):
        visibility = get_visibility(self.sequences, obj)
        anim_loc, anim_rot, anim_scale, is_animated = self.is_animated_ugg(obj, settings)
        root = War3Object(obj.name)

        if parent is not None:
            root.parent = parent

        root.pivot = settings.global_matrix @ Vector(obj.location)
        root.anim_loc = anim_loc
        root.anim_scale = anim_scale
        root.anim_rot = anim_rot
        register_global_sequence(self.global_seqs, root.anim_scale)

        if root.anim_loc is not None:
            register_global_sequence(self.global_seqs, root.anim_loc)
            if obj.parent is not None:
                transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
                              root.anim_loc.handles_left, obj.parent.matrix_world.inverted())

            transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
                          root.anim_loc.handles_left, settings.global_matrix)

        if root.anim_rot is not None:
            register_global_sequence(self.global_seqs, root.anim_rot)
            if obj.parent is not None:
                transform_rot(root.anim_rot.keyframes, obj.parent.matrix_world.inverted())

            transform_rot(root.anim_rot.keyframes, settings.global_matrix)

        root.visibility = visibility
        register_global_sequence(self.global_seqs, visibility)
        root.billboarded = billboarded
        root.billboard_lock = billboard_lock
        self.objects['bone'].add(root)
        for b in obj.pose.bones:
            bone = War3Object(b.name)
            if b.parent is not None:
                bone.parent = b.parent.name
            else:
                bone.parent = root.name

            bone.pivot = obj.matrix_world @ Vector(b.bone.head_local)  # Armature space to world space
            bone.pivot = settings.global_matrix @ Vector(bone.pivot)  # Axis conversion
            data_path = 'pose.bones[\"' + b.name + '\"].%s'
            bone.anim_loc = War3AnimationCurve.get(obj.animation_data, data_path % 'location', 3, self.sequences)
            # get_curves(obj, data_path % 'location', (0, 1, 2))

            if settings.optimize_animation and bone.anim_loc is not None:
                bone.anim_loc.optimize(settings.optimize_tolerance, self.sequences)

            bone.anim_rot = War3AnimationCurve.get(obj.animation_data, data_path % 'rotation_quaternion', 4, self.sequences)
            # get_curves(obj, data_path % 'rotation_quaternion', (0, 1, 2, 3))

            if bone.anim_rot is None:
                bone.anim_rot = War3AnimationCurve.get(obj.animation_data, data_path % 'rotation_euler', 3, self.sequences)

            if settings.optimize_animation and bone.anim_rot is not None:
                bone.anim_rot.optimize(settings.optimize_tolerance, self.sequences)

            bone.anim_scale = War3AnimationCurve.get(obj.animation_data, data_path % 'scale', 3, self.sequences)
            # get_curves(obj, data_path % 'scale', (0, 1, 2))

            if settings.optimize_animation and bone.anim_scale is not None:
                bone.anim_scale.optimize(settings.optimize_tolerance, self.sequences)

            register_global_sequence(self.global_seqs, bone.anim_scale)

            if bone.anim_loc is not None:
                m = obj.matrix_world @ b.bone.matrix_local
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                              bone.anim_loc.handles_left, settings.global_matrix @ m.to_3x3().to_4x4())
                register_global_sequence(self.global_seqs, bone.anim_loc)

            if bone.anim_rot is not None:
                mat_pose_ws = obj.matrix_world @ b.bone.matrix_local
                mat_rest_ws = obj.matrix_world @ b.matrix
                transform_rot(bone.anim_rot.keyframes, mat_pose_ws)
                transform_rot(bone.anim_rot.keyframes, settings.global_matrix)
                register_global_sequence(self.global_seqs, bone.anim_rot)

            self.objects['bone'].add(bone)

    def add_lights(self, billboard_lock, billboarded, obj, settings):
        visibility = get_visibility(self.sequences, obj)
        light = War3Object(obj.name)
        light.object = obj
        light.pivot = settings.global_matrix @ Vector(obj.location)
        light.billboarded = billboarded
        light.billboard_lock = billboard_lock

        if hasattr(obj.data, "mdl_light"):
            light_data = obj.data.mdl_light
            light.type = light_data.light_type

            light.intensity = light_data.intensity
            light.intensity_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.intensity', 1, self.sequences)
            # get_curve(obj.data, ['mdl_light.intensity'])

            register_global_sequence(self.global_seqs, light.intensity_anim)

            light.atten_start = light_data.atten_start
            light.atten_start_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.atten_start', 1, self.sequences)
            # get_curve(obj.data, ['mdl_light.atten_start'])

            register_global_sequence(self.global_seqs, light.atten_start_anim)

            light.atten_end = light_data.atten_end
            light.atten_end_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.atten_end', 1, self.sequences)
            # get_curve(obj.data, ['mdl_light.atten_end'])

            register_global_sequence(self.global_seqs, light.atten_end_anim)

            light.color = light_data.color
            light.color_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.color', 3, self.sequences)
            # get_curve(obj.data, ['mdl_light.color'])

            register_global_sequence(self.global_seqs, light.color_anim)

            light.amb_color = light_data.amb_color
            light.amb_color_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.amb_color', 3, self.sequences)
            # get_curve(obj.data, ['mdl_light.amb_color'])

            register_global_sequence(self.global_seqs, light.amb_color_anim)

            light.amb_intensity = light_data.amb_intensity
            light.amb_intensity_anim = War3AnimationCurve.get(obj.data.animation_data, 'mdl_light.amb_intensity', 1, self.sequences)
            # get_curve(obj.data, ['obj.mdl_light.amb_intensity'])

            register_global_sequence(self.global_seqs, light.amb_intensity_anim)

        light.visibility = visibility
        register_global_sequence(self.global_seqs, visibility)
        self.objects['light'].add(light)

    def create_collision_shapes(self, obj, parent, settings):
        collider = War3Object(obj.name)
        collider.parent = parent
        collider.pivot = settings.global_matrix @ Vector(obj.location)
        if 'Box' in obj.name:
            collider.type = 'Box'
            corners = []
            for corner in ((0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
                           (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)):
                mat = settings.global_matrix @ obj.matrix_world
                corners.append(mat.to_quaternion() @ Vector(
                    abs(x * obj.empty_display_size * settings.global_matrix.median_scale) * y for x, y in
                    zip(obj.scale, corner)))

            vmin, vmax = calc_extents(corners)

            collider.verts = [vmin, vmax]  # TODO: World space or relative to pivot??
            self.objects['collisionshape'].add(collider)
        elif 'Sphere' in obj.name:
            collider.type = 'Sphere'
            collider.verts = [settings.global_matrix @ Vector(obj.location)]
            collider.radius = settings.global_matrix.median_scale * max(
                abs(x * obj.empty_display_size) for x in obj.scale)
            self.objects['collisionshape'].add(collider)

    @staticmethod
    def calc_bounds_radius(min_ext, max_ext):
        x = (max_ext[0] - min_ext[0])/2
        y = (max_ext[1] - min_ext[1])/2
        z = (max_ext[2] - min_ext[2])/2
        return math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))

    @staticmethod
    def calc_extents(vertices):
        max_extents = tuple(max(vertices, key=itemgetter(i))[i] for i in range(3))
        min_extents = tuple(min(vertices, key=itemgetter(i))[i] for i in range(3))

        return min_extents, max_extents
