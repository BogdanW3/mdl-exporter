import itertools

from ..War3Material import War3Material
from ..War3MaterialLayer import War3MaterialLayer
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


def from_scene(war3_model: War3Model, context, settings):

    scene = context.scene

    if settings.use_actions:
        war3_model.sequences = get_actions(war3_model.f2ms)
        space_actions(war3_model.sequences)
    else:
        war3_model.sequences = get_sequences(war3_model.f2ms, scene)

    objs = []
    mats = set()

    if settings.use_selection:
        objs = (obj for obj in scene.objects if obj.select_get() and obj.visible_get())
    else:
        objs = (obj for obj in scene.objects if obj.visible_get())

    for obj in objs:
        parent = get_parent(obj)

        billboarded = False
        billboard_lock = (False, False, False)
        if hasattr(obj, "mdl_billboard"):
            bb = obj.mdl_billboard
            billboarded = bb.billboarded
            billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)
            # NOTE: Axes are listed backwards (same as with colors)

        # Animations
        visibility = get_visibility(war3_model.sequences, obj)

        # Particle Systems
        if len(obj.particle_systems):
            add_particle_systems(war3_model, billboard_lock, billboarded, mats, obj, parent, settings)

        # Collision Shapes
        elif obj.type == 'EMPTY' and obj.name.startswith('Collision'):
            create_collision_shapes(war3_model, obj, parent, settings)

        elif obj.type == 'MESH' or obj.type == 'CURVE':
            make_mesh(war3_model, billboard_lock, billboarded, context, mats, obj, parent, settings)

        elif obj.type == 'EMPTY':
            add_empties_animations(war3_model, billboard_lock, billboarded, obj, parent, settings)

        elif obj.type == 'ARMATURE':
            add_bones(war3_model, billboard_lock, billboarded, obj, parent, settings)

        elif obj.type in ('LAMP', 'LIGHT'):
            add_lights(war3_model, billboard_lock, billboarded, obj, settings)

        elif obj.type == 'CAMERA':
            war3_model.cameras.append(obj)

    war3_model.geosets = list(war3_model.geoset_map.values())
    war3_model.materials = [War3Material.get(mat, war3_model) for mat in mats]

    # Add default material if no other materials present
    if any((x for x in war3_model.geosets if x.mat_name == "default")):
        default_mat = War3Material("default")
        default_mat.layers.append(War3MaterialLayer())
        war3_model.materials.append(default_mat)

    war3_model.materials = sorted(war3_model.materials, key=lambda x: x.priority_plane)

    layers = list(itertools.chain.from_iterable([material.layers for material in war3_model.materials]))
    war3_model.textures = list(set((layer.texture for layer in layers)))
    # Convert to set and back to list for unique entries

    # Demote bones to helpers if they have no attached geosets
    for bone in war3_model.objects['bone']:
        if not any([g for g in war3_model.geosets if bone.name in itertools.chain.from_iterable(g.matrices)]):
            war3_model.objects['helper'].add(bone)

    war3_model.objects['bone'] -= war3_model.objects['helper']
    # We also need the textures used by emitters
    for particle_sys in list(war3_model.objects['particle']) + list(war3_model.objects['particle2']) + list(war3_model.objects['ribbon']):
        if particle_sys.emitter.texture_path not in war3_model.textures:
            war3_model.textures.append(particle_sys.emitter.texture_path)

    war3_model.tvertex_anims = list(set((layer.texture_anim for layer in layers if layer.texture_anim is not None)))

    vertices_all = []

    war3_model.objects_all = []
    war3_model.object_indices = {}

    index = 0
    for tag in ('bone', 'light', 'helper', 'attachment', 'particle', 'particle2', 'ribbon', 'eventobject', 'collisionshape'):
        for object in war3_model.objects[tag]:
            war3_model.object_indices[object.name] = index
            war3_model.objects_all.append(object)
            vertices_all.append(object.pivot)
            if tag == 'collisionshape':
                for vert in object.verts:
                    vertices_all.append(vert)
            index = index+1

    for geoset in war3_model.geosets:
        for vertex in geoset.vertices:
            vertices_all.append(vertex[0])

        geoset.min_extent, geoset.max_extent = calc_extents([x[0] for x in geoset.vertices])

        if geoset.geoset_anim is not None:
            register_global_sequence(war3_model.global_seqs, geoset.geoset_anim.alpha_anim)
            register_global_sequence(war3_model.global_seqs, geoset.geoset_anim.color_anim)

            for bone in itertools.chain.from_iterable(geoset.matrices):
                war3_model.geoset_anim_map[bone] = geoset.geoset_anim

    # Account for particle systems when calculating bounds
    for particle_sys in list(war3_model.objects['particle']) + list(war3_model.objects['particle2']) + list(war3_model.objects['ribbon']):
        vertices_all.append(tuple(x + y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)))
        vertices_all.append(tuple(x - y/2 for x, y in zip(particle_sys.pivot, particle_sys.dimensions)))

    war3_model.geoset_anims = list(set(g.geoset_anim for g in war3_model.geosets if g.geoset_anim is not None))

    war3_model.global_extents_min, war3_model.global_extents_max = calc_extents(vertices_all) if len(vertices_all) else ((0, 0, 0), (0, 0, 0))
    war3_model.global_seqs = sorted(war3_model.global_seqs)
