import itertools
from typing import List, Dict, Set

import bpy
from mathutils import Vector, Matrix

from .create_material_stuff import get_new_material2
from .make_bones import parse_armatures
from ..War3AnimationAction import War3AnimationAction
from ..War3Camera import War3Camera
from ..War3CollisionShape import War3CollisionShape
from ..War3Emitter import War3Emitter
from ..War3ExportSettings import War3ExportSettings
from ..War3Helper import War3Helper
from ..War3Material import War3Material
from ..War3Layer import War3Layer
from ..War3Model import War3Model
from .add_empties_animations import get_event, get_helper, get_bone, get_attachment, get_collision
from .add_lights import get_lights
from .add_particle_systems import get_particle_emitter, get_particle_emitter2, get_ribbon_emitter
from .get_actions import get_actions
from ..War3Node import War3Node
from .make_mesh import create_geoset, get_geoset_anim, create_geoset_bone, create_armature_bone
from ..War3Texture import War3Texture
from ..bpy_helpers.BpySceneObjects import BpySceneObjects
from ...utils import calc_extents


def from_scene(context: bpy.types.Context,
               settings: War3ExportSettings) -> War3Model:
    print("context: ", context)

    print("from_scene!")

    bpy_scene_objects = BpySceneObjects(context, settings)

    frame2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
    model_name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")
    war3_model = War3Model(model_name)

    sequences, actions = get_actions(frame2ms, bpy_scene_objects.actions,
                                     settings.use_actions, bpy_scene_objects.sequences)
    war3_model.sequences.extend(sequences)

    parse_bpy_objects2(bpy_scene_objects, settings, war3_model, actions)

    for bpy_geoset in bpy_scene_objects.geosets:
        print("creating geoset from: " + bpy_geoset.name)
        if bpy_geoset.self_as_parent:
            war3_model.bones.append(create_geoset_bone(bpy_geoset, actions,
                                                       war3_model.sequences, war3_model.global_seqs,
                                                       settings))
        elif bpy_geoset.no_vgs and bpy_geoset.parent_name not in [b.name for b in war3_model.bones]:
            war3_model.bones.append(create_armature_bone(bpy_geoset, actions,
                                                         war3_model.sequences, war3_model.global_seqs,
                                                         settings))
        war_geoset = create_geoset(bpy_geoset)
        war3_model.geosets.append(war_geoset)

        for i in range(0, len(war_geoset.matrices)):
            for j in range(0, len(war_geoset.matrices[i])):
                if war_geoset.matrices[i][j] == "":
                    war_geoset.matrices[i][j] = war3_model.bones[0].name

        # Needs fixing. supposed to make sure that the 4 first weights adds up to 255.
        # if settings.use_skinweights:
        #     bone_zero: str = war3_model.bones[0].name
        #     for vertex in war_geoset.vertices:
        #         fix_skin_bones(vertex.bone_list, vertex.weight_list, bone_zero)
        if bpy_geoset.bpy_material and bpy_geoset.bpy_material.node_tree:
            geo_anim = get_geoset_anim(bpy_geoset, actions, war3_model.sequences, war3_model.global_seqs)
            war_geoset.geoset_anim = geo_anim
            if geo_anim:
                geo_anim.geoset = war_geoset
                geo_anim.geoset_id = len(war3_model.geosets)-1

    for bpy_material in bpy_scene_objects.materials:
        use_const_color = any([g for g in war3_model.geosets
                               if g.mat_name == bpy_material.name
                               and g.geoset_anim is not None
                               and any((g.geoset_anim.color, g.geoset_anim.color_anim))])
        new_material = get_new_material2(bpy_material, settings.use_skinweights, use_const_color, actions,
                                         war3_model.sequences, war3_model.global_seqs)
        war3_model.materials.append(new_material)

    # Add default material if no other materials present
    if any((x for x in war3_model.geosets if x.mat_name == "default")):
        default_mat = War3Material("default")
        war_layer = War3Layer()
        war_layer.texture = War3Texture()
        default_mat.layers.append(war_layer)
        war3_model.materials.append(default_mat)

    war3_model.materials = sorted(war3_model.materials, key=lambda x: x.priority_plane)

    layers = list(itertools.chain.from_iterable([material.layers for material in war3_model.materials]))
    war3_model.textures.extend(set((layer.texture for layer in layers)))
    war3_model.textures_paths.extend(set((layer.texture_path for layer in layers)))
    war3_model.tvertex_anims.extend(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))
    # Convert to set and back to list for unique entries

    if settings.demote_to_helper:
        # Demote bones to helpers if they have no attached geosets
        demote_to_helpers(war3_model)

    # We also need the textures used by emitters
    emitters: List[War3Emitter] = []
    emitters.extend(war3_model.particle_systems)
    emitters.extend(war3_model.particle_systems2)
    emitters.extend(war3_model.particle_ribbon)
    # for particle_sys in emitters:
    #     if particle_sys.emitter.texture_path not in war3_model.textures_paths:
    #         # war3_model.textures.append(War3Texture(particle_sys.emitter.texture_path))
    #         war3_model.textures.append(particle_sys.texture)
    #         war3_model.textures_paths.append(particle_sys.emitter.texture_path)
    for particle_sys in war3_model.particle_systems2:
        if particle_sys.emitter.texture_path not in war3_model.textures_paths:
            war3_model.textures.append(particle_sys.texture)
            war3_model.textures_paths.append(particle_sys.emitter.texture_path)

    collect_all_nodes(war3_model)

    vertices_all: List[List[float]] = []
    vertices_all.extend(collect_all_pos(war3_model.objects_all))

    for geoset in war3_model.geosets:
        for vertex in geoset.vertices:
            vertices_all.append(vertex.pos)

        geoset.min_extent, geoset.max_extent = calc_extents([vert.pos for vert in geoset.vertices])

        if geoset.geoset_anim is not None:
            for bone in itertools.chain.from_iterable(geoset.matrices):
                war3_model.geoset_anim_map[bone] = geoset.geoset_anim

    # # Account for particle systems when calculating bounds
    # for particle_sys in list(war3_model.particle_systems) + list(war3_model.particle_systems2) + list(war3_model.particle_ribbon):
    #     vertices_all.append([x + y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)])
    #     vertices_all.append([x - y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)])

    war3_model.geoset_anims = list(set(g.geoset_anim for g in war3_model.geosets if g.geoset_anim is not None))

    war3_model.global_extents_min, war3_model.global_extents_max \
        = calc_extents(vertices_all) if len(vertices_all) else ([0, 0, 0], [0, 0, 0])
    war3_model.global_seqs = sorted(war3_model.global_seqs)

    return war3_model


def demote_to_helpers(war3_model: War3Model):
    used_bones: Set[str] = set()
    for geoset in war3_model.geosets:
        for m in geoset.matrices:
            for name in m:
                used_bones.add(name)
    bone_to_helper: Dict[War3Node, War3Node] = {}
    for bone in war3_model.bones:
        if bone.name not in used_bones:
            # print("demoting", bone.name, "to helper")
            helper = War3Helper(bone.name, bone.obj_id, bone.pivot,
                                bone.parent_id, bone.parent,
                                bone.anim_loc, bone.anim_rot, bone.anim_scale,
                                bone.bindpose)
            helper.parent_node = bone.parent_node
            helper.billboard_lock = bone.billboard_lock
            helper.billboarded = bone.billboarded
            helper.bindpose = bone.bindpose
            war3_model.helpers.append(helper)
            bone_to_helper[bone] = helper

    for node in (n for n in war3_model.bones if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.lights if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.helpers if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.attachments if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.particle_systems if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.particle_systems2 if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.particle_ribbon if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.event_objects if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]
    for node in (n for n in war3_model.collision_shapes if n.parent_node in bone_to_helper):
        node.parent_node = bone_to_helper[node.parent_node]

    for bone in bone_to_helper.keys():
        war3_model.bones.remove(bone)


def collect_all_nodes(war3_model: War3Model):
    model_objects_all = war3_model.objects_all
    model_objects_all.extend(war3_model.bones)
    model_objects_all.extend(war3_model.lights)
    model_objects_all.extend(war3_model.helpers)
    model_objects_all.extend(war3_model.attachments)
    model_objects_all.extend(war3_model.particle_systems)
    model_objects_all.extend(war3_model.particle_systems2)
    model_objects_all.extend(war3_model.particle_ribbon)
    model_objects_all.extend(war3_model.event_objects)
    model_objects_all.extend(war3_model.collision_shapes)

    for i, war3_node in enumerate(model_objects_all):
        # print("Setting nodeID: ", i, war3_node.name)
        war3_node.obj_id = i

    for war3_node in model_objects_all:
        if war3_node.parent_node is not None:
            # print("setting parent id to", war3_node.parent_node.obj_id,
            #       "for", war3_node.name, "\t(", war3_node.parent_node.name, ")")
            war3_node.parent_id = war3_node.parent_node.obj_id


def collect_all_pos(model_objects_all: List[War3Node]) -> List[List[float]]:
    pos_all: List[List[float]] = []
    for war3_node in model_objects_all:
        pos_all.append(war3_node.pivot)
        if isinstance(war3_node, War3CollisionShape):
            for vert in war3_node.verts:
                pos_all.append(vert)
    return pos_all


def parse_bpy_objects2(bpy_scene_objects: BpySceneObjects,
                       settings: War3ExportSettings,
                       war3_model: War3Model,
                       actions: List[bpy.types.Action]):
    global_matrix: Matrix = settings.global_matrix
    global_scale: float = settings.scale
    optimize_animation: bool = settings.optimize_animation
    optimize_tolerance: float = settings.optimize_tolerance if optimize_animation else -1
    sequences: List[War3AnimationAction] = war3_model.sequences
    global_seqs: Set[int] = war3_model.global_seqs

    print("parse_bpy_objects2!")
    war3_model.bones.extend(parse_armatures(bpy_scene_objects, global_matrix,
                                            optimize_tolerance, actions,
                                            sequences, global_seqs))

    for bpy_empty_node in bpy_scene_objects.collisions:
        war3_model.collision_shapes.append(get_collision(bpy_empty_node, global_matrix))

    for bpy_emitter in bpy_scene_objects.particle1s:
        particle_emitter = get_particle_emitter(sequences, global_seqs, actions, bpy_emitter,
                                                optimize_tolerance,
                                                global_matrix)
        war3_model.particle_systems.append(particle_emitter)

    for bpy_emitter in bpy_scene_objects.particle2s:
        emitter_ = get_particle_emitter2(sequences, global_seqs, actions, bpy_emitter,
                                         optimize_tolerance,
                                         global_matrix, global_scale)
        war3_model.particle_systems2.append(emitter_)

    for bpy_emitter in bpy_scene_objects.ribbons:
        ribbon_emitter = get_ribbon_emitter(sequences, global_seqs, actions, bpy_emitter,
                                            optimize_tolerance,
                                            global_matrix)
        validMaterials = [m for m in war3_model.materials if (m.name == ribbon_emitter.emitter.ribbon_material.name)]
        if 0 < len(validMaterials):
            ribbon_emitter.material = validMaterials[0]
        elif 0 < len(war3_model.materials):
            ribbon_emitter.material = war3_model.materials[0]
        war3_model.particle_ribbon.append(ribbon_emitter)

    for bpy_light in bpy_scene_objects.lights:
        light = get_lights(sequences, global_seqs, actions, bpy_light, global_matrix)
        war3_model.lights.append(light)

    for bpy_empty_node in bpy_scene_objects.events:
        event = get_event(sequences, global_seqs, actions, bpy_empty_node,
                          optimize_tolerance, global_matrix)
        war3_model.event_objects.append(event)

    for bpy_empty_node in bpy_scene_objects.helpers:
        if bpy_empty_node.should_be_bone:
            bone = get_bone(sequences, global_seqs, actions, bpy_empty_node,
                            optimize_tolerance, global_matrix)
            war3_model.bones.append(bone)
        else:
            helper = get_helper(sequences, global_seqs, actions, bpy_empty_node,
                                optimize_tolerance, global_matrix)
            war3_model.helpers.append(helper)

    for bpy_empty_node in bpy_scene_objects.attachments:
        attachment = get_attachment(sequences, global_seqs, actions, bpy_empty_node,
                                    optimize_tolerance, global_matrix)
        war3_model.attachments.append(attachment)

    for bpy_obj in bpy_scene_objects.cameras:
        camera = get_camera(bpy_obj, global_matrix, global_scale)
        war3_model.cameras.append(camera)


def get_camera(bpy_obj: bpy.types.Object, global_matrix: Matrix, global_scale: float):
    camera = War3Camera(bpy_obj.name)

    camera.pivot = global_matrix @ Vector(bpy_obj.location)
    camera.field_of_view = bpy_obj.data.angle
    camera.far_clip = bpy_obj.data.clip_end * global_scale
    camera.near_clip = bpy_obj.data.clip_start * global_scale

    if bpy_obj.data.dof.focus_object is None:
        targetDist = bpy_obj.data.dof.focus_distance
        camera.target = global_matrix @ bpy_obj.matrix_world @ Vector([0, 0, -targetDist])
    else:
        camera.target = global_matrix @ bpy_obj.data.dof.focus_object.location
    camera.bindpose = bpy_obj.matrix_basis

    return camera


def fix_skin_bones(bone_list: List[str], weight_list: List[int], bone_zero: str):
    # Warcraft 800+ do support vertex (skin) weights;
    # 4 bone bindings per vertex whose weight sum up to 255
    # This will ensure that the weight of the (up to) 4 first bones sums up to 255
    numBones = len(weight_list)

    # Ugly fix to make sure total weight is 255

    tot_weight = sum(weight_list[:min(4, numBones)])
    w_conv = 255.0 / tot_weight
    weight_adjust = 255
    for i in range(numBones):
        weight_list[i] = round(i * w_conv)
        weight_adjust -= weight_list[i]

    if len(weight_list) == 1 or weight_list[1] - weight_adjust < 0 and 0 < (weight_list[1] - weight_adjust):
        print("ugg")

    if weight_adjust < 0 and 1 < len(weight_list) and 0 < (weight_list[1] - weight_adjust):
        print("ugg2")


def fix_skin_bones1(bone_list: List[str], weight_list: List[int], bone_zero: str):
    # Warcraft 800+ do support vertex (skin) weights;
    # 4 bone bindings per vertex whose weight sum up to 255
    # This will ensure that the weight of the (up to) 4 first bones sums up to 255
    numBones = len(weight_list)
    weight_list_temp = weight_list[:min(4, numBones)]

    tot_weight = sum(weight_list_temp)
    w_conv = 255.0 / tot_weight
    weight_list_temp = [round(i * w_conv) for i in weight_list_temp]
    # Ugly fix to make sure total weight is 255

    weight_adjust = 255 - sum(weight_list_temp)
    weight_list[0] = int(weight_list[0] + weight_adjust)

    # bone_list = bone_list[:min(4, numBones)]
    # if numBones < 4:
    #     print("not enough bones:", numBones)
    #     for i in range(4-numBones):
    #         print("adding bone!")
    #         bone_list.append(bone_zero)
    #         weight_list.append(0)
