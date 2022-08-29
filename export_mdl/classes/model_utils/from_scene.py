import itertools
import typing
from typing import List, Union

import bpy

from .create_material_stuff import get_new_material
from ..War3CollisionShape import War3CollisionShape
from ..War3Emitter import War3Emitter
from ..War3ExportSettings import War3ExportSettings
from ..War3Material import War3Material
from ..War3Layer import War3Layer
from ..War3Model import War3Model
from .add_bones import add_bones
from .add_empties_animations import add_empties_animations
from .add_lights import add_lights
from .add_particle_systems import add_particle_systems
from .create_collision_shapes import create_collision_shapes
from .get_parent import get_parent
from .get_sequences import get_sequences
from .get_actions import get_actions
from ..animation_curve_utils.space_actions import space_actions
from .get_visibility import get_visibility
from .make_mesh import make_mesh
from .register_global_sequence import register_global_sequence
from ...utils import calc_extents


def from_scene(context: bpy.types.Context,
               settings: War3ExportSettings) -> War3Model:
    print("context: ", context)

    scene: bpy.types.Scene = context.scene

    frame2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
    model_name = bpy.path.basename(context.blend_data.filepath).replace(".blend", "")
    war3_model = War3Model(model_name)

    if settings.use_actions:
        war3_model.sequences = get_actions(frame2ms)
        space_actions(war3_model.sequences)
    else:
        war3_model.sequences = get_sequences(frame2ms, scene)

    objects: List[bpy.types.Object]
    # objects: Union[List[bpy.types.Object], bpy.types.bpy_prop_collection, bpy.types.SceneObjects] = []
    materials: typing.Set[bpy.types.Material] = set()

    if settings.use_selection:
        objects = list(obj for obj in scene.objects if obj.select_get() and obj.visible_get())
    else:
        objects = list(obj for obj in scene.objects if obj.visible_get())

    parse_bpy_objects(context, materials, objects, settings, war3_model)

    war3_model.geosets = list(war3_model.geoset_map.values())
    # war3_model.materials = [War3Material.get(mat, war3_model) for mat in materials]
    war3_model.materials = [get_new_material(mat, war3_model) for mat in materials]

    # Add default material if no other materials present
    if any((x for x in war3_model.geosets if x.mat_name == "default")):
        default_mat = War3Material("default")
        default_mat.layers.append(War3Layer())
        war3_model.materials.append(default_mat)

    war3_model.materials = sorted(war3_model.materials, key=lambda x: x.priority_plane)

    layers = list(itertools.chain.from_iterable([material.layers for material in war3_model.materials]))
    war3_model.textures = list(set((layer.texture for layer in layers)))
    # Convert to set and back to list for unique entries

    # # Demote bones to helpers if they have no attached geosets
    # for bone in war3_model.objects['bone']:
    #     if not any([geoset for geoset in war3_model.geosets if bone.name in itertools.chain.from_iterable(geoset.matrices)]):
    #         war3_model.objects['helper'].add(bone)

    # war3_model.objects['bone'] -= war3_model.objects['helper']

    # We also need the textures used by emitters
    emitters: List[War3Emitter] = []
    emitters.extend(war3_model.particle_systems)
    emitters.extend(war3_model.particle_systems2)
    emitters.extend(war3_model.particle_ribbon)
    for particle_sys in emitters:
        if particle_sys.emitter.texture_path not in war3_model.textures:
            war3_model.textures.append(particle_sys.emitter.texture_path)

    ugg = list(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))
    war3_model.tvertex_anims = list(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))

    vertices_all = []

    war3_model.objects_all = []
    war3_model.object_indices = {}

    index = 0
    object_indices = war3_model.object_indices
    model_objects_all = war3_model.objects_all
    # for tag in ('bone', 'light', 'helper', 'attachment', 'particle', 'particle2', 'ribbon', 'eventobject', 'collisionshape'):
    #     for model_object in war3_model.objects[tag]:
    #         object_indices[model_object.name] = index
    #         model_objects_all.append(model_object)
    #         vertices_all.append(model_object.pivot)
    #         if tag == 'collisionshape':
    #             for vert in model_object.verts:
    #                 vertices_all.append(vert)
    #         index = index+1
    #
    # for tag in ('bone', 'light', 'helper', 'attachment', 'particle', 'particle2', 'ribbon', 'eventobject', 'collisionshape'):
    #     pass
    for model_object in war3_model.bones:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.lights:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.helpers:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.attachments:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.particle_systems:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.particle_systems2:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.particle_ribbon:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.event_objects:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)
    for model_object in war3_model.collision_shapes:
        index = collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all)

    for geoset in war3_model.geosets:
        for vertex in geoset.vertices:
            vertices_all.append(vertex.pos)

        geoset.min_extent, geoset.max_extent = calc_extents([vert.pos for vert in geoset.vertices])

        if geoset.geoset_anim is not None:
            register_global_sequence(war3_model.global_seqs, geoset.geoset_anim.alpha_anim)
            register_global_sequence(war3_model.global_seqs, geoset.geoset_anim.color_anim)

            for bone in itertools.chain.from_iterable(geoset.matrices):
                war3_model.geoset_anim_map[bone] = geoset.geoset_anim

    # Account for particle systems when calculating bounds
    for particle_sys in list(war3_model.particle_systems) + list(war3_model.particle_systems2) + list(war3_model.particle_ribbon):
        vertices_all.append(tuple(x + y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)))
        vertices_all.append(tuple(x - y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)))

    war3_model.geoset_anims = list(set(g.geoset_anim for g in war3_model.geosets if g.geoset_anim is not None))

    war3_model.global_extents_min, war3_model.global_extents_max = calc_extents(vertices_all) if len(vertices_all) else ((0, 0, 0), (0, 0, 0))
    war3_model.global_seqs = sorted(war3_model.global_seqs)

    return war3_model


def collect_all_nodes(index, model_object, model_objects_all, object_indices, vertices_all):
    object_indices[model_object.name] = index
    model_objects_all.append(model_object)
    vertices_all.append(model_object.pivot)
    if isinstance(model_object, War3CollisionShape):
        for vert in model_object.verts:
            vertices_all.append(vert)
    return index + 1


def parse_bpy_objects(context: bpy.types.Context,
                      materials: typing.Set[bpy.types.Material],
                      #objects: Union[List[bpy.types.Object], bpy.types.bpy_prop_collection, bpy.types.SceneObjects],
                      objects: List[bpy.types.Object],
                      settings: War3ExportSettings,
                      war3_model: War3Model):
    for bpy_obj in objects:
        parent: typing.Optional[bpy.types.Object] = get_parent(bpy_obj)

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
            add_particle_systems(war3_model, billboard_lock, billboarded, materials, bpy_obj, parent, settings)

        # Collision Shapes
        elif bpy_obj.type == 'EMPTY' and bpy_obj.name.startswith('Collision'):
            create_collision_shapes(war3_model, bpy_obj, parent, settings)

        elif bpy_obj.type == 'MESH' or bpy_obj.type == 'CURVE':
            make_mesh(war3_model, billboard_lock, billboarded, context, materials, bpy_obj, parent, settings)

        elif bpy_obj.type == 'EMPTY':
            add_empties_animations(war3_model, billboard_lock, billboarded, bpy_obj, parent, settings)

        elif bpy_obj.type == 'ARMATURE':
            add_bones(war3_model.sequences, war3_model.global_seqs, war3_model.bones, billboard_lock, billboarded, bpy_obj, parent, settings)

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
