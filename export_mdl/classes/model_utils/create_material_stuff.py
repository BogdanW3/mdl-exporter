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
    shader = getattr(bpy_material, "mdl_shader", 'AUTO')

    mdl_layers: List[War3MaterialLayerProperties] = bpy_material.mdl_layers
    for i, layer_settings in enumerate(mdl_layers):
        material.layers.append(parse_layer(i, layer_settings, bpy_material, sequences, actions, global_seqs))

    hd = shader in ('HD', 'CRYSTAL')
    if not len(material.layers):
        from_nodes = layers_from_mat_nodes(bpy_material, hd)
        if from_nodes is not None:
            material.layers.extend(from_nodes)
            # Automatic: HD with HD skinning on, when the nodes have PBR textures (normal, ORM or emissive)
            if shader == 'AUTO' and use_skin_weights and 1 < len(from_nodes):
                hd = True
        else:
            layer = War3Layer()
            layer.texture = War3Texture()
            material.layers.append(layer)

    if hd:
        pad_hd_slots(material.layers)
        shader_id = 24 if shader == 'CRYSTAL' else 1
        for layer in material.layers:
            layer.hd = True
            layer.shader = shader_id

    return material


# Textures an HD material falls back on for slots it doesn't fill
HD_DEFAULT_TEXTURES = ("Textures\\white.blp", "Textures\\normal.dds", "Textures\\orm.dds",
                       "Textures\\Black32.dds", "ReplaceableId 1", "ReplaceableTextures\\EnvironmentMap.dds")


def pad_hd_slots(layers: List[War3Layer]):
    # An HD material always binds all six PBR slots
    for slot in range(len(layers), len(HD_DEFAULT_TEXTURES)):
        path = HD_DEFAULT_TEXTURES[slot]
        layers.append(get_layer(path, 1 if path.startswith("ReplaceableId") else 0))


def layers_from_mat_nodes(bpy_material: bpy.types.Material, hd: bool = False):
    if bpy_material.use_nodes \
            and bpy_material.node_tree \
            and bpy_material.node_tree.nodes \
            and bpy_material.node_tree.nodes.get("Principled BSDF"):
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
        # Blender 4.0 renamed the Principled BSDF "Emission" input to "Emission Color"
        emis_path = get_path("Emission Color", socket_to_filePath) or get_path("Emission", socket_to_filePath)
        if hd or norm_path or orm_path or emis_path:
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
    layer.unfogged = layer_settings.unfogged
    layer.sphere_env_map = layer_settings.sphere_env_map
    layer.wrap_width = layer_settings.wrap_width
    layer.wrap_height = layer_settings.wrap_height
    layer.unlit = layer_settings.unlit
    layer.back_faces_for_shadows = layer_settings.back_faces_for_shadows
    layer.ambient_occlusion = layer_settings.ambient_occlusion

    layer.emissive_gain = layer_settings.emissive_gain
    layer.fresnel_color = tuple(layer_settings.fresnel_color)
    layer.fresnel_opacity = layer_settings.fresnel_opacity
    layer.fresnel_team_color = layer_settings.fresnel_team_color
    layer.emissive_gain_anim = get_wc3_animation_curve('mdl_layers[%d].emissive_gain' % i, actions, 1,
                                                       sequences, global_seqs)
    layer.fresnel_color_anim = get_wc3_animation_curve('mdl_layers[%d].fresnel_color' % i, actions, 3,
                                                       sequences, global_seqs)
    layer.fresnel_opacity_anim = get_wc3_animation_curve('mdl_layers[%d].fresnel_opacity' % i, actions, 1,
                                                         sequences, global_seqs)
    layer.fresnel_team_color_anim = get_wc3_animation_curve('mdl_layers[%d].fresnel_team_color' % i, actions, 1,
                                                            sequences, global_seqs)

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
