import itertools
from typing import List, Union, Dict, Set, Optional, Tuple

import bpy
from mathutils import Vector, Matrix

from .create_material_stuff import get_new_material2
from ..War3AnimationAction import War3AnimationAction
from ..War3Bone import War3Bone
from ..War3CollisionShape import War3CollisionShape
from ..War3Emitter import War3Emitter
from ..War3ExportSettings import War3ExportSettings
from ..War3Helper import War3Helper
from ..War3Material import War3Material
from ..War3Layer import War3Layer
from ..War3Model import War3Model
from .add_bones import add_bones
from .add_empties_animations import create_and_add_from_empty, create_event, create_helper, create_attachment
from .add_lights import add_lights
from .add_particle_systems import add_particle_systems
from .create_collision_shapes import create_collision_shapes
from .get_parent import get_parent
from .get_sequences import get_sequences, get_sequences2
from .get_actions import get_actions, get_actions2
from ..War3Node import War3Node
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from ..animation_curve_utils.space_actions import space_actions
from .get_visibility import get_visibility
from .make_mesh2 import make_mesh, make_geosets, create_geoset
from .register_global_sequence import register_global_sequence
from ..bpy_helpers.bpy_scene_helper import BpySceneObjects
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec1
from ...utils import calc_extents


def from_scene(context: bpy.types.Context,
               settings: War3ExportSettings) -> War3Model:
    print("context: ", context)

    bpy_scene_objects = BpySceneObjects(context, settings)

    frame2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
    model_name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")
    war3_model = War3Model(model_name)

    if settings.use_actions:
        war3_model.sequences = get_actions2(frame2ms, bpy_scene_objects.actions)
        space_actions(war3_model.sequences)
    else:
        war3_model.sequences = get_sequences2(frame2ms, bpy_scene_objects.sequences)

    parse_bpy_objects2(bpy_scene_objects, settings, war3_model)

    for bpy_geoset in bpy_scene_objects.geosets:
        print("creating geoset!")
        war3_model.geosets.append(create_geoset(bpy_geoset, bpy_scene_objects.bone_names))

    for bpy_material in bpy_scene_objects.materials:
        use_const_color = any([g for g in war3_model.geosets
                               if g.mat_name == bpy_material.name
                               and g.geoset_anim is not None
                               and any((g.geoset_anim.color, g.geoset_anim.color_anim))])
        new_material = get_new_material2(bpy_material, use_const_color, war3_model.sequences, war3_model.global_seqs)
        war3_model.materials.append(new_material)


    # Add default material if no other materials present
    if any((x for x in war3_model.geosets if x.mat_name == "default")):
        default_mat = War3Material("default")
        default_mat.layers.append(War3Layer())
        war3_model.materials.append(default_mat)

    war3_model.materials = sorted(war3_model.materials, key=lambda x: x.priority_plane)

    layers = list(itertools.chain.from_iterable([material.layers for material in war3_model.materials]))
    war3_model.textures.extend(set((layer.texture for layer in layers)))
    war3_model.textures_paths.extend(set((layer.texture_path for layer in layers)))
    war3_model.tvertex_anims.extend(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))
    # Convert to set and back to list for unique entries

    # Demote bones to helpers if they have no attached geosets
    demote_to_helpers(war3_model)

    # We also need the textures used by emitters
    emitters: List[War3Emitter] = []
    emitters.extend(war3_model.particle_systems)
    emitters.extend(war3_model.particle_systems2)
    emitters.extend(war3_model.particle_ribbon)
    for particle_sys in emitters:
        if particle_sys.emitter.texture_path not in war3_model.textures:
            war3_model.textures.append(particle_sys.emitter.texture_path)
            war3_model.textures_paths.append(particle_sys.emitter.texture_path)

    vertices_all: List[List[float]] = []

    object_indices = war3_model.object_indices
    model_objects_all = war3_model.objects_all

    collect_all_pos(model_objects_all, object_indices, vertices_all, war3_model)

    for geoset in war3_model.geosets:
        for vertex in geoset.vertices:
            vertices_all.append(vertex.pos)

        geoset.min_extent, geoset.max_extent = calc_extents([vert.pos for vert in geoset.vertices])

        if geoset.geoset_anim is not None:
            for bone in itertools.chain.from_iterable(geoset.matrices):
                war3_model.geoset_anim_map[bone] = geoset.geoset_anim

    # Account for particle systems when calculating bounds
    for particle_sys in list(war3_model.particle_systems) + list(war3_model.particle_systems2) + list(war3_model.particle_ribbon):
        vertices_all.append([x + y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)])
        vertices_all.append([x - y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)])

    war3_model.geoset_anims = list(set(g.geoset_anim for g in war3_model.geosets if g.geoset_anim is not None))

    war3_model.global_extents_min, war3_model.global_extents_max = calc_extents(vertices_all) if len(vertices_all) else [[0, 0, 0], [0, 0, 0]]
    war3_model.global_seqs = sorted(war3_model.global_seqs)

    return war3_model


def demote_to_helpers(war3_model):
    bones_to_remove = []
    for bone in war3_model.bones:
        if not any([geoset for geoset in war3_model.geosets if
                    bone.name in itertools.chain.from_iterable(geoset.matrices)]):
            helper = War3Helper(bone.name, bone.anim_loc, bone.anim_rot, bone.anim_scale, bone.parent, bone.pivot)
            helper.billboard_lock = bone.billboard_lock
            helper.billboarded = bone.billboarded
            helper.bindpose = bone.bindpose
            war3_model.helpers.append(helper)
            bones_to_remove.append(bone)
    for bone in bones_to_remove:
        war3_model.bones.remove(bone)


def collect_all_pos(model_objects_all, object_indices, vertices_all, war3_model):
    index = 0
    for war3_node in war3_model.bones:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.lights:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.helpers:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.attachments:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.particle_systems:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.particle_systems2:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.particle_ribbon:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.event_objects:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)
    for war3_node in war3_model.collision_shapes:
        index = collect_all_nodes(index, war3_node, model_objects_all, object_indices, vertices_all)


def collect_all_nodes(index: int,
                      model_object: War3Node,
                      model_objects_all: List[War3Node],
                      object_indices: Dict[str, int],
                      vertices_all: List[List[float]]):
    object_indices[model_object.name] = index
    model_objects_all.append(model_object)
    vertices_all.append(model_object.pivot)
    if isinstance(model_object, War3CollisionShape):
        for vert in model_object.verts:
            vertices_all.append(vert)
    return index + 1


def parse_bpy_objects(context: bpy.types.Context,
                      objects: List[bpy.types.Object],
                      bpy_scene_objects: BpySceneObjects,
                      settings: War3ExportSettings,
                      war3_model: War3Model):
    for bpy_obj in objects:
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)

        parent_name: Optional[str] = None if parent is None else parent.name
        if parent is not None:
            c_parent = parent.name
        else:
            c_parent = None

        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
            # NOTE: Axes are listed backwards (same as with colors)

        # Animations
        visibility = get_visibility(war3_model.sequences, bpy_obj)

        # Particle Systems
        if len(bpy_obj.particle_systems):
            add_particle_systems(war3_model, billboard_lock, billboarded, set(), bpy_obj, parent_name, settings)

        # Collision Shapes
        elif bpy_obj.type == 'EMPTY' and bpy_obj.name.startswith('Collision'):
            war3_model.collision_shapes.append(create_collision_shapes(bpy_obj, parent_name, settings))

        elif bpy_obj.type == 'MESH' or bpy_obj.type == 'CURVE':
            make_mesh(war3_model, bpy_scene_objects, billboard_lock, billboarded, context, set(), bpy_obj, parent_name, settings)

        elif bpy_obj.type == 'EMPTY':
            create_and_add_from_empty(war3_model, billboard_lock, billboarded, bpy_obj, parent, settings)

        elif bpy_obj.type == 'ARMATURE':
            print("bpy_obj: ", bpy_obj)
            print("   isArmature: ", isinstance(bpy_obj, bpy.types.Armature))
            add_bones(war3_model.sequences, war3_model.global_seqs, war3_model.bones, billboard_lock, billboarded, bpy_obj, parent_name, settings)

        elif bpy_obj.type in ('LAMP', 'LIGHT'):
            if isinstance(bpy_obj, bpy.types.Light):
                print("is Light")
            if isinstance(bpy_obj, bpy.types.PointLight):
                print("is PointLight")
            if isinstance(bpy_obj, bpy.types.SunLight):
                print("is SunLight")
            add_lights(war3_model, billboard_lock, billboarded, bpy_obj, settings)

        elif bpy_obj.type == 'CAMERA':
            war3_model.cameras.append(bpy_obj)


def parse_bpy_objects2(bpy_scene_objects: BpySceneObjects,
                       settings: War3ExportSettings,
                       war3_model: War3Model):
    global_matrix = settings.global_matrix
    sequences = war3_model.sequences
    global_seqs = war3_model.global_seqs
    for armature in bpy_scene_objects.bpy_objects['Armature']:
        animation_data: bpy.types.AnimData = armature.animation_data
        matrix_world = Matrix(armature.matrix_world)
        for pose_bone in bpy_scene_objects.bpy_nodes[armature.name][1]:
            bone = get_wc3_bone(animation_data, global_matrix, global_seqs, matrix_world, pose_bone, sequences,
                                settings.optimize_animation,
                                settings.optimize_tolerance)

            war3_model.bones.append(bone)

    for bpy_obj in bpy_scene_objects.bpy_objects['Collision']:
        # Collision Shapes
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        war3_model.collision_shapes.append(create_collision_shapes(bpy_obj, parent_name, settings))

    for bpy_obj in bpy_scene_objects.bpy_objects['ParticleEmitter']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        add_particle_systems(war3_model, billboard_lock, billboarded, set(), bpy_obj, parent_name, settings)

    for bpy_obj in bpy_scene_objects.bpy_objects['ParticleEmitter2']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        add_particle_systems(war3_model, billboard_lock, billboarded, set(), bpy_obj, parent_name, settings)

    for bpy_obj in bpy_scene_objects.bpy_objects['RibbonEmitter']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        add_particle_systems(war3_model, billboard_lock, billboarded, set(), bpy_obj, parent_name, settings)

    for bpy_obj in bpy_scene_objects.bpy_objects['Light']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        add_lights(war3_model, billboard_lock, billboarded, bpy_obj, settings)

    for bpy_obj in bpy_scene_objects.bpy_objects['EventObject']:
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        event = create_event(sequences, global_seqs, bpy_obj, parent_name, settings)
        war3_model.event_objects.append(event)

    for bpy_obj in bpy_scene_objects.bpy_objects['Helper']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        helper = create_helper(sequences, global_seqs, billboard_lock, billboarded, bpy_obj, parent_name, settings)
        war3_model.helpers.append(helper)

    for bpy_obj in bpy_scene_objects.bpy_objects['Attachment']:
        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        attachment = create_attachment(sequences, global_seqs, billboard_lock, billboarded, bpy_obj, parent_name, settings)
        war3_model.helpers.append(attachment)

    for bpy_obj in bpy_scene_objects.bpy_objects['Camera']:
        parent: Optional[bpy.types.Object] = get_parent(bpy_obj)
        parent_name: Optional[str] = None if parent is None else parent.name
        war3_model.cameras.append(bpy_obj)


def add_bones(sequences: List[War3AnimationAction], global_seqs: Set[int], bones: List[War3Bone],
              billboard_lock: Tuple[bool, bool, bool],
              billboarded: bool,
              bpy_obj: bpy.types.Object,
              settings: War3ExportSettings):

    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    matrix_world = Matrix(bpy_obj.matrix_world)
    global_matrix = settings.global_matrix
    for pose_bone in bpy_obj.pose.bones:
        bone = get_wc3_bone(animation_data, global_matrix, global_seqs, matrix_world, pose_bone, sequences,
                            settings.optimize_animation,
                            settings.optimize_tolerance)

        bones.append(bone)


def get_wc3_bone(animation_data: bpy.types.AnimData,
                 global_matrix: Matrix,
                 global_seqs: Set[int],
                 matrix_world: Matrix,
                 pose_bone: bpy.types.PoseBone,
                 sequences: List[War3AnimationAction], optimize_animation: bool,
                 optimize_tolerance: float):
    data_path = 'pose.bones[\"' + pose_bone.name + '\"].%s'
    anim_loc, anim_rot, anim_scale = get_animation_data(animation_data, pose_bone, data_path, global_matrix,
                                                        global_seqs,
                                                        matrix_world, sequences, optimize_animation,
                                                        optimize_tolerance)
    b_parent = pose_bone.parent
    bone_p_name = None if b_parent is None else b_parent.name
    pivot_ = matrix_world @ Vector(pose_bone.bone.head_local)  # Armature space to world space
    pivot = global_matrix @ Vector(pivot_)  # Axis conversion
    bone = War3Bone(pose_bone.name, anim_loc, anim_rot, anim_scale, bone_p_name, pivot)
    return bone


def get_animation_data(animation_data: bpy.types.AnimData,
                       pose_bone: bpy.types.PoseBone,
                       data_path:str,
                       global_matrix: Matrix,
                       global_seqs: Set[int],
                       matrix_world: Matrix,
                       sequences: List[War3AnimationAction],
                       optimize_animation: bool,
                       optimize_tolerance: float):
    anim_loc = get_wc3_animation_curve(animation_data, data_path % 'location', 3, sequences)
    anim_rot_quat = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
    anim_rot_euler = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
    anim_rot = anim_rot_quat if anim_rot_quat is not None else anim_rot_euler
    anim_scale = get_wc3_animation_curve(animation_data, data_path % 'scale', 3, sequences)
    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if optimize_animation:
        if anim_loc is not None:
            anim_loc.optimize(optimize_tolerance, sequences)

        if anim_rot is not None:
            anim_rot.optimize(optimize_tolerance, sequences)

        if anim_scale is not None:
            anim_scale.optimize(optimize_tolerance, sequences)

    if anim_loc is not None:
        m = matrix_world @ pose_bone.bone.matrix_local
        to__x_ = m.to_3x3().to_4x4()
        x_ = global_matrix @ to__x_
        transform_vec1(anim_loc, x_)
    if anim_rot is not None:
        mat_pose_ws = matrix_world @ pose_bone.bone.matrix_local
        # mat_rest_ws = matrix_world @ b.matrix
        transform_rot(anim_rot.keyframes, mat_pose_ws)
        transform_rot(anim_rot.keyframes, global_matrix)
    return anim_loc, anim_rot, anim_scale