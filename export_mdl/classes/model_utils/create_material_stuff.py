from typing import List, Tuple, Dict, Union, Optional, Set

import bpy
from bpy.types import Collection
from bpy_types import PropertyGroup

from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Geoset import War3Geoset
from export_mdl.classes.War3Material import War3Material
from export_mdl.classes.War3Layer import War3Layer
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Texture import War3Texture
from export_mdl.classes.War3TextureAnim import War3TextureAnim
from export_mdl.classes.animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from export_mdl.properties import War3MaterialLayerProperties


def get_new_material(bpy_material: bpy.types.Material, geosets: List[War3Geoset], sequences: List[War3AnimationAction], global_seqs: Set[int]):
    material = War3Material(bpy_material.name)

    for geoset in geosets:
        if geoset.geoset_anim is not None and geoset.mat_name == bpy_material.name:
            if any((geoset.geoset_anim.color, geoset.geoset_anim.color_anim)):
                material.use_const_color = True

    material.priority_plane = bpy_material.priority_plane

    mdl_layers: List[War3MaterialLayerProperties] = bpy_material.mdl_layers
    for i, layer_settings in enumerate(mdl_layers):
        material.layers.append(parse_layer(i, layer_settings, bpy_material, sequences, global_seqs))

    if not len(material.layers):
        material.layers.append(War3Layer())

    return material


def get_new_material2(bpy_material: bpy.types.Material, use_const_color: bool, sequences: List[War3AnimationAction], global_seqs: Set[int]):
    material = War3Material(bpy_material.name)
    material.use_const_color = use_const_color

    material.priority_plane = bpy_material.priority_plane

    mdl_layers: List[War3MaterialLayerProperties] = bpy_material.mdl_layers
    for i, layer_settings in enumerate(mdl_layers):
        material.layers.append(parse_layer(i, layer_settings, bpy_material, sequences, global_seqs))

    if not len(material.layers):
        material.layers.append(War3Layer())

    return material


def parse_layer(i: int,
                layer_settings: War3MaterialLayerProperties,
                mat: bpy.types.Material,
                sequences: List[War3AnimationAction],
                global_seqs: Set[int]):
    print("parse layer2")
    layer = War3Layer()
    texture_path = layer_settings.path

    if layer_settings.texture_type == '0':
        layer.texture_path = texture_path
        layer.texture = War3Texture(texture_path)
    else:
        layer.texture_path = "ReplaceableId %s" % layer_settings.texture_type
        layer.texture = War3Texture("ReplaceableId %s" % layer_settings.replaceable_id, layer_settings.texture_type)

    if layer_settings.texture_type == '36':
        layer.texture_path = "ReplaceableId %s" % layer_settings.replaceable_id
        layer.texture = War3Texture("ReplaceableId %s" % layer_settings.replaceable_id, layer_settings.replaceable_id)

    layer.filter_mode = layer_settings.filter_mode
    layer.unshaded = layer_settings.unshaded
    layer.two_sided = layer_settings.two_sided
    layer.no_depth_test = layer_settings.no_depth_test
    layer.no_depth_set = layer_settings.no_depth_set
    layer.alpha_value = layer_settings.alpha
    animation_data = mat.animation_data
    layer.alpha_anim = get_wc3_animation_curve(animation_data, 'mdl_layers[%d].alpha' % i, 1, sequences)
    # get_curve(mat, {'mdl_layers[%d].alpha' % i})
    if mat.use_nodes:
        uv_node: Optional[bpy.types.Node] = mat.node_tree.nodes.get(layer_settings.name)
        animation_data = mat.node_tree.animation_data
        texture_anim = get_texture_anim(animation_data, sequences, global_seqs, uv_node)
        if texture_anim is not None:
            layer.texture_anim = texture_anim
        # uv_node = mat.node_tree.nodes.get(layer_settings.name)
        # if uv_node is not None and mat.node_tree.animation_data is not None:
        #     layer.texture_anim = War3TextureAnim.get(mat.node_tree.animation_data, uv_node, sequences)
    return layer


def get_texture_anim(animation_data: Optional[bpy.types.AnimData],
                     sequences: List[War3AnimationAction],
                     global_seqs: Set[int],
                     uv_node: Optional[bpy.types.Node]) -> Optional[War3TextureAnim]:
    if uv_node is not None and animation_data is not None:
        if animation_data.action:
            loc_value: str
            rot_value: str
            scl_value: str
            if len(uv_node.inputs) > 1:  # 2.81 Mapping Node
                loc_value = 'nodes["%s"].inputs["Location"].default_value'
                rot_value = 'nodes["%s"].inputs["Rotation"].default_value'
                scl_value = 'nodes["%s"].inputs["Scale"].default_value'
            else:
                loc_value = 'nodes["%s"].translation'
                rot_value = 'nodes["%s"].rotation'
                scl_value = 'nodes["%s"].scale'
            translation = get_wc3_animation_curve(animation_data, loc_value % uv_node.name, 3, sequences)
            rotation = get_wc3_animation_curve(animation_data, rot_value % uv_node.name, 3, sequences)
            scale = get_wc3_animation_curve(animation_data, scl_value % uv_node.name, 3, sequences)
            if any((translation, rotation, scale)):
                texture_anim = War3TextureAnim()
                texture_anim.set_from(translation, rotation, scale)

                register_global_sequence(global_seqs, translation)
                register_global_sequence(global_seqs, rotation)
                register_global_sequence(global_seqs, scale)

                return texture_anim
    return None


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)
