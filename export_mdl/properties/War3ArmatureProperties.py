from typing import List, Dict

import bpy

from export_mdl.properties.War3ArmatureSequenceListItem import War3ArmatureSequenceListItem

ACTION_NAME_UNANIMATED = '#UNANIMATED'


def set_animation(armature_prop: 'War3ArmatureProperties', context: bpy.types.Context):
    print("set_animation?", armature_prop, context)

    seq_prop = armature_prop.sequencesList[armature_prop.sequencesListIndex]
    animation_name = seq_prop.name
    animation_length: int
    if len(animation_name) and not bpy.data.actions.get(animation_name):
        bpy.data.actions.new(animation_name)

    if len(animation_name) and bpy.data.actions.get(animation_name):
        print("has", animation_name)
        animation_length = seq_prop.length
        prepare_action(context, animation_name, animation_length)
        for bpy_object in bpy.context.scene.objects:
            object_action = bpy.data.actions.get(animation_name + ' ' + bpy_object.name)
            if object_action:
                if bpy_object.animation_data is None:
                    bpy_object.animation_data_create()
                bpy_object.animation_data.action = object_action
    else:
        print("did not find", animation_name)


    tl_m = context.scene.timeline_markers
    print("tl_m.__dict__:", dict(tl_m))

    print("context.scene.timeline_markers:", tl_m, ", size:", len(tl_m), ", sizeV:", len(tl_m.values()), ", sizeK:", len(tl_m.keys()))
    print("context.scene.timeline_markers.get(Stand):", tl_m.get("Stand"))
    print("context.scene.timeline_markers.find(Stand):", tl_m.find("Stand"))
    print("context.scene.timeline_markers.count(Stand):", tl_m.values().count(tl_m.get("Stand")))

    markers: Dict[str, List[int]] = {}
    for tl in tl_m:
        marker_instances = markers.get(tl.name, [])
        marker_instances.append(tl.frame)
        markers[tl.name] = marker_instances
        print(tl, tl.frame, tl.camera)
    for tl in tl_m:
        print(tl, tl.items())
    for tl in tl_m.keys():
        print(tl)
        print(tl_m.get(tl), tl_m.get(tl).frame)


def prepare_action(context: bpy.types.Context, animation_name: str, anim_length: int):
    armature_object = context.object
    if armature_object.animation_data is None:
        armature_object.animation_data_create()
    bpy_action = bpy.data.actions.get(animation_name)
    armature_object.animation_data.action = bpy_action
    print(animation_name, 0, "-", anim_length)
    print("armature_object.animation_data.action:", armature_object.animation_data.action)
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = anim_length


class War3ArmatureProperties(bpy.types.PropertyGroup):
    sequencesList: bpy.props.CollectionProperty(type=War3ArmatureSequenceListItem)
    sequencesListIndex: bpy.props.IntProperty(update=set_animation)

    @classmethod
    def register(cls):
        bpy.types.Armature.war_3 = bpy.props.PointerProperty(type=War3ArmatureProperties, options={'HIDDEN'})

    @classmethod
    def unregister(cls):
        del bpy.types.Armature.war_3
