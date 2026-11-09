# Attachments, event objects, collision shapes and lights become objects of their own (not armature bones),
# tagged with their node type so the exporter writes them back as the same kind of node.
#
# Layout, matching how the exporter reads them back:
# - the node's pivot is the object's delta location, its location/rotation/scale keys are the file's own
#   translation/rotation/scaling tracks (so a key is exactly the file's value);
# - the object is parented to its parent node (a bone, or another node object) with that parent's rest
#   transform cancelled out, so its keys are in model space like the file's.
from typing import Dict, List, Set

import bpy
from mathutils import Matrix, Vector

from .create_collision_empties import set_collision_display
from .create_light_objects import create_bpy_light
from .create_armature_object import apply_billboard
from .key_tracks import key_track, compatible_quaternions

NODE_TYPE_KEY = "mdl_node_type"


def armature_node_names(model) -> Set[str]:
    """Nodes that become armature bones: bones, helpers, anything a skin or matrix group refers to (HD skins can
    weight vertices to any node), and their ancestors."""
    names = {node.name for node in list(model.bones) + list(model.helpers)}
    for geoset in model.geosets:
        for group in geoset.matrices:
            names.update(str(name) for name in group)
    by_name = {node.name: node for node in model.id_to_object.values()}
    for name in list(names):
        node = by_name.get(name)
        while node is not None and node.parent:
            names.add(node.parent)
            node = by_name.get(node.parent)
    return {name for name in names if name in by_name}


def create_node_objects(model, bpy_armature_object: bpy.types.Object, bone_size: float, frame_time: float):
    print(" creating attachments, events, collision shapes and lights")
    if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bone_names = {bone.name for bone in bpy_armature_object.data.bones}
    durations = getattr(model, "global_sequence_durations", [])

    created: Dict[str, bpy.types.Object] = {}
    pending = []
    for kind, nodes in (('ATTACHMENT', model.attachments), ('EVENT', model.event_objects),
                        ('COLLISION', model.collision_shapes), ('LIGHT', model.lights)):
        for node in nodes:
            if node.name in bone_names:
                continue  # A skin deforms with it, so it stays a bone
            obj = create_object(kind, node, bone_size)
            obj[NODE_TYPE_KEY] = kind
            # Blender object names are unique, a model's node names don't have to be (an attachment and an
            # event object can share one); the exporter uses this name
            obj["mdl_node_name"] = node.name
            if getattr(node, "path", ""):
                obj["mdl_attachment_path"] = node.path
            if hasattr(obj, "mdl_billboard"):
                apply_billboard(obj.mdl_billboard, node)
            obj.rotation_mode = 'QUATERNION'
            obj.delta_location = Vector(node.pivot)
            obj.location = (0.0, 0.0, 0.0)
            created[node.name] = obj
            pending.append((node, obj))

    by_name = {node.name: node for node in model.id_to_object.values()}
    for node, obj in pending:
        parent_to(obj, node.parent, bpy_armature_object, bone_names, created, by_name)
        animate(obj, node, frame_time, model.sequences, durations)
    return [obj for _, obj in pending]


def create_object(kind: str, node, bone_size: float) -> bpy.types.Object:
    if kind == 'LIGHT':
        obj = create_bpy_light(node)
    else:
        obj = bpy.data.objects.new(node.name, None)
        bpy.context.scene.collection.objects.link(obj)
        obj.empty_display_size = bone_size
        obj.empty_display_type = {'ATTACHMENT': 'CONE', 'EVENT': 'CIRCLE'}.get(kind, 'PLAIN_AXES')
        if kind == 'COLLISION':
            set_collision_display(obj, node)
    return obj


def parent_to(obj: bpy.types.Object, parent_name, armature_obj: bpy.types.Object, bone_names: Set[str],
              created: Dict[str, bpy.types.Object], by_name):
    if not parent_name:
        return
    if parent_name in bone_names:
        bone = armature_obj.data.bones[parent_name]
        obj.parent = armature_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = parent_name
        # Bone parenting attaches at the tail
        rest = armature_obj.matrix_world @ bone.matrix_local @ Matrix.Translation((0.0, bone.length, 0.0))
        obj.matrix_parent_inverse = rest.inverted()
    elif parent_name in created:
        obj.parent = created[parent_name]
        # A node object rests at its pivot (its parents' rest transforms are cancelled the same way)
        parent_pivot = by_name[parent_name].pivot if parent_name in by_name else (0.0, 0.0, 0.0)
        obj.matrix_parent_inverse = Matrix.Translation(Vector(parent_pivot)).inverted()


def animate(obj: bpy.types.Object, node, frame_time: float, sequences, durations: List[int]):
    def setter(path):
        return lambda value: setattr(obj, path, value)
    key_track(obj, 'location', node.anim_loc, frame_time, sequences, durations, (0.0, 0.0, 0.0),
              setter('location'), lambda v: tuple(v[:3]), "Transform")
    compatible_quaternions(node.anim_rot)
    key_track(obj, 'rotation_quaternion', node.anim_rot, frame_time, sequences, durations, (1.0, 0.0, 0.0, 0.0),
              setter('rotation_quaternion'), lambda v: tuple(v[:4]), "Transform")
    key_track(obj, 'scale', node.anim_scale, frame_time, sequences, durations, (1.0, 1.0, 1.0),
              setter('scale'), lambda v: tuple(v[:3]), "Transform")
    # Visibility: render visibility, hidden below half
    key_track(obj, 'hide_render', getattr(node, 'visibility', None), frame_time, sequences, durations, False,
              setter('hide_render'), lambda v: v[0] < 0.5, "Visibility", interpolation='CONSTANT')
    if obj.type == 'LIGHT' and hasattr(obj.data, 'mdl_light'):
        # Animated light values go on the light datablock, like the static ones
        settings = obj.data.mdl_light
        for prop in ('intensity', 'atten_start', 'atten_end', 'amb_intensity', 'shadow_casting_start',
                     'shadow_casting_end', 'quadratic_falloff', 'linear_falloff', 'damping'):
            key_track(obj.data, 'mdl_light.' + prop, getattr(node, prop + '_anim', None), frame_time, sequences,
                      durations, getattr(settings, prop), lambda v, p=prop: setattr(settings, p, v),
                      lambda v: v[0], "Light")
        for prop in ('color', 'amb_color'):
            key_track(obj.data, 'mdl_light.' + prop, getattr(node, prop + '_anim', None), frame_time, sequences,
                      durations, tuple(getattr(settings, prop)), lambda v, p=prop: setattr(settings, p, v),
                      lambda v: tuple(v[:3]), "Light")
    times = getattr(node, 'event_times', None)
    if times:
        obj["event_track"] = 1.0
        for time in times:
            obj.keyframe_insert(data_path='["event_track"]', frame=round(time / frame_time), group="Event")
