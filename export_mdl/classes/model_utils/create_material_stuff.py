import re
from typing import List, Tuple, Dict, Union, Optional, Set

import bpy

from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Material import War3Material
from export_mdl.classes.War3Layer import War3Layer
from export_mdl.classes.War3Texture import War3Texture
from export_mdl.classes.War3TextureAnim import War3TextureAnim
from export_mdl.classes.animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from export_mdl.properties import War3MaterialLayerProperties


def get_new_material2(bpy_material: bpy.types.Material,
                      use_const_color: bool,
                      use_skin_weights: bool,
                      actions: List[bpy.types.Action],
                      sequences: List[War3AnimationAction],
                      global_seqs: Set[int]):
    material = War3Material(bpy_material.name)
    material.use_const_color = use_const_color

    material.priority_plane = bpy_material.priority_plane

    mdl_layers: List[War3MaterialLayerProperties] = bpy_material.mdl_layers
    for i, layer_settings in enumerate(mdl_layers):
        material.layers.append(parse_layer(i, layer_settings, bpy_material, sequences, actions, global_seqs))

    if not len(material.layers):
        from_nodes = layers_from_mat_nodes(bpy_material)
        if from_nodes is not None:
            if use_skin_weights:
                material.is_hd = True
            material.layers.extend(from_nodes)
        else:
            layer = War3Layer()
            layer.texture = War3Texture()
            material.layers.append(layer)

    return material


def layers_from_mat_nodes(bpy_material: bpy.types.Material):
    if bpy_material.use_nodes and bpy_material.node_tree and bpy_material.node_tree.nodes:
        link_dict_bw: Dict[bpy.types.Node, List[bpy.types.NodeLink]] = {}
        links: List[bpy.types.NodeLink] = bpy_material.node_tree.links
        for link in links:
            to_node: bpy.types.Node = link.to_node
            if to_node:
                if to_node not in link_dict_bw:
                    link_dict_bw[to_node] = []
                link_dict_bw[to_node].append(link)

        nodes = bpy_material.node_tree.nodes
        shader_node: bpy.types.Node = nodes.get("Principled BSDF")
        inputs: List[bpy.types.NodeSocket] = shader_node.inputs

        socket_to_filePath: Dict[str, List[str]] = {}
        for inp in inputs:
            texNodes: List[str] = []
            max_search = len(nodes)
            inp_links = inp.links
            link = inp.links[0] if 0 < len(inp_links) else None
            collect_tex_nodes(link, link_dict_bw, texNodes, max_search)

            socket_to_filePath[inp.name] = texNodes

        layers: List[War3Layer] = []
        diff_texs = socket_to_filePath.get("Base Color")
        if 1 < len(diff_texs):
            to_remove = []
            for tex in diff_texs:
                if re.match(".*_norm(al)?\\.\\w{3,4}$", tex) \
                        or re.match(".*_orm\\.\\w{3,4}$", tex):
                    to_remove.append(tex)
            if len(to_remove) != len(diff_texs):
                for tex in to_remove:
                    diff_texs.remove(tex)

        diff_path = get_path("Base Color", socket_to_filePath)
        layers.append(get_layer(diff_path, 0, "Textures\\white.blp"))
        norm_path = get_path("Normal", socket_to_filePath)
        orm_path = get_path("Roughness", socket_to_filePath)
        if orm_path is None:
            orm_path = get_path("Metallic", socket_to_filePath)
        if orm_path is None:
            orm_path = get_path("Specular", socket_to_filePath)
        emis_path = get_path("Emission", socket_to_filePath)
        if norm_path or orm_path or emis_path:
            layers.append(get_layer(norm_path, 0, "Textures\\normal.dds"))
            layers.append(get_layer(orm_path, 0, "Textures\\orm.dds"))
            layers.append(get_layer(emis_path, 0, "Textures\\Black32.dds"))
            layers.append(get_layer("ReplaceableId %s" % 1, 1))
            layers.append(get_layer(get_path("Specular Tint", socket_to_filePath), 0, "ReplaceableTextures\\EnvironmentMap.dds"))
        return layers
    return None


def get_path(socket: str, socket_to_filePath: Dict[str, List[str]]):
    if socket is not None \
            and socket_to_filePath.get(socket) is not None \
            and 0 < len(socket_to_filePath.get(socket)):
        return socket_to_filePath.get(socket)[0]
    return None


def get_layer(texture_path: str, replaceable_id: int, alt_path: str = None):
    layer = War3Layer()
    if texture_path is None:
        texture_path = alt_path
    print("\t LayerTexturePath: ", texture_path)
    layer.texture = War3Texture(texture_path, replaceable_id)
    layer.texture_path = texture_path
    return layer


def collect_tex_nodes(curr_link: bpy.types.NodeLink,
                      link_dict: Dict[bpy.types.Node, List[bpy.types.NodeLink]],
                      file_paths: List[str],
                      max_checks: int):
    if 0 < max_checks and curr_link is not None:
        from_node = curr_link.from_node
        if isinstance(from_node, bpy.types.ShaderNodeTexImage) and from_node.image is not None:
            file_paths.append(from_node.image.filepath)
        elif from_node is not None and link_dict.get(from_node) is not None:
            for link in link_dict.get(from_node):
                collect_tex_nodes(link, link_dict, file_paths, max_checks-1)


def parse_layer(i: int,
                layer_settings: War3MaterialLayerProperties,
                mat: bpy.types.Material,
                sequences: List[War3AnimationAction],
                actions: List[bpy.types.Action],
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
    alpha_anim = get_wc3_animation_curve('mdl_layers[%d].alpha' % i, actions, 1, sequences, global_seqs)
    layer.alpha_anim = alpha_anim

    # get_curve(mat, {'mdl_layers[%d].alpha' % i})
    if mat.use_nodes:
        uv_node: Optional[bpy.types.Node] = mat.node_tree.nodes.get(layer_settings.name)
        animation_data = mat.node_tree.animation_data
        texture_anim = get_texture_anim(animation_data, sequences, actions, global_seqs, uv_node)
        if texture_anim is not None:
            layer.texture_anim = texture_anim
        # uv_node = mat.node_tree.nodes.get(layer_settings.name)
        # if uv_node is not None and mat.node_tree.animation_data is not None:
        #     layer.texture_anim = War3TextureAnim.get(mat.node_tree.animation_data, uv_node, sequences)
    return layer


def get_texture_anim(animation_data: Optional[bpy.types.AnimData],
                     sequences: List[War3AnimationAction],
                     actions: List[bpy.types.Action],
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
            translation = get_wc3_animation_curve(loc_value % uv_node.name, actions, 3, sequences, global_seqs)

            rotation = get_wc3_animation_curve(rot_value % uv_node.name, actions, 3, sequences, global_seqs)

            scale = get_wc3_animation_curve(scl_value % uv_node.name, actions, 3, sequences, global_seqs)

            if any((translation, rotation, scale)):
                texture_anim = War3TextureAnim()
                texture_anim.set_from(translation, rotation, scale)

                return texture_anim
    return None


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)
