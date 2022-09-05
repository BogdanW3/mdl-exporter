import os
from pathlib import Path
from typing import List, Dict

import bpy

from export_mdl import constants
from export_mdl.classes.War3Material import War3Material
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Texture import War3Texture
from export_mdl.properties.War3Preferences import War3Preferences


def create_material(model: War3Model, team_color: str) -> Dict[str, bpy.types.Material]:
    print("creating materials")
    preferences: War3Preferences = bpy.context.preferences.addons.get('export_mdl').preferences

    folders = get_folders(preferences.alternativeResourceFolder, preferences.resourceFolder, model.file)
    texture_ext = get_texture_ext(preferences.textureExtension)

    bpy_images: Dict[str, bpy.types.Image] = {}
    for texture in model.textures:
        bpy_image = get_image(folders, team_color, texture, texture_ext)
        bpy_images[texture.texture_path] = bpy_image

    bpy_materials: Dict[str, bpy.types.Material] = {}
    for i, material in enumerate(model.materials):
        print("material #" + str(i), material)
        bpy_images_of_layer: List[bpy.types.Image] = []
        for layer in material.layers:
            bpy_images_of_layer.append(bpy_images[layer.texture.texture_path])

        bpy_material = create_bpy_material(bpy_images_of_layer, material)

        bpy_materials[str(i)] = bpy_material

    return bpy_materials


def create_bpy_material(bpy_images_of_layer: List[bpy.types.Image], material: War3Material):
    material_name = bpy_images_of_layer[-1].filepath.split(os.path.sep)[-1].split('.')[0]
    bpy_material: bpy.types.Material = bpy.data.materials.new(name=material_name)
    bpy_material.shadow_method = 'NONE'
    bpy_material.use_nodes = True

    bpy_material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    texture_slot_index = 0
    material_node_tree = bpy_material.node_tree
    shader_node: bpy.types.Node = material_node_tree.nodes.get("Principled BSDF")
    color_input_socket = shader_node.inputs.get("Base Color")
    node_width: float = shader_node.width
    if material.is_hd:
        bpy_material.blend_method = 'HASHED'
        bpy_material.shadow_method = 'HASHED'
        diffuse = material_node_tree.nodes.new('ShaderNodeMixRGB')
        diffuse.location.x -= node_width + 50
        diffuse.blend_type = 'COLOR'

        for i, bpy_image in enumerate(bpy_images_of_layer):
            texture_mat_node = get_new_node(node_width + 350, 200 - 200 * i, material_node_tree, 'ShaderNodeTexImage')
            texture_mat_node.image = bpy_image
            if i == 0:
                material_node_tree.links.new(texture_mat_node.outputs.get("Color"), diffuse.inputs.get("Color1"))
                material_node_tree.links.new(diffuse.outputs.get("Color"), color_input_socket)
                material_node_tree.links.new(texture_mat_node.outputs.get("Alpha"), shader_node.inputs.get("Alpha"))
            elif i == 1:
                normal_map = get_new_node(node_width + 50, 200 - 200 * i, material_node_tree, 'ShaderNodeNormalMap')
                material_node_tree.links.new(texture_mat_node.outputs.get("Color"), normal_map.inputs.get("Color"))
                material_node_tree.links.new(normal_map.outputs.get("Normal"), shader_node.inputs.get("Normal"))
            elif i == 2:
                orm = get_new_node(node_width + 50, 200 - 200 * i, material_node_tree, 'ShaderNodeSeparateRGB')

                roughthness_inv = get_new_node(node_width, 200 - 200 * i, material_node_tree, "ShaderNodeMath")
                roughthness_inv.operation = 'SUBTRACT'
                roughthness_inv.inputs[0].default_value = 1


                material_node_tree.links.new(texture_mat_node.outputs.get("Color"), orm.inputs.get("Image"))
                # I don't currently know how to do occlusion
                material_node_tree.links.new(orm.outputs.get("G"), roughthness_inv.inputs[1])
                material_node_tree.links.new(roughthness_inv.outputs[0], shader_node.inputs.get("Roughness"))
                material_node_tree.links.new(orm.outputs.get("B"), shader_node.inputs.get("Metallic"))
                material_node_tree.links.new(texture_mat_node.outputs.get("Alpha"), diffuse.inputs.get("Fac"))
            elif i == 3:
                material_node_tree.links.new(texture_mat_node.outputs.get("Color"), shader_node.inputs.get("Emission"))
            elif i == 4:
                team_color = get_new_node(node_width + diffuse.width + 50, 0, material_node_tree, 'ShaderNodeRGB')
                team_color.outputs[0].default_value = (1, 0, 0, 1)
                material_node_tree.links.new(team_color.outputs.get("Color"), diffuse.inputs.get("Color2"))
            # else:
            # skip the environmental map, possibly change the world's map to it
            print(bpy_image.filepath, " at place ", i)
    else:
        for i, bpy_image in enumerate(bpy_images_of_layer):
            texture_mat_node = get_new_node(node_width + 50, 200 - 100 * i, material_node_tree, 'ShaderNodeTexImage')
            texture_mat_node.image = bpy_image
            material_node_tree.links.new(texture_mat_node.outputs.get("Color"), color_input_socket)
    return bpy_material


def get_new_node(loc_x: float,
                 loc_y: float,
                 material_node_tree: bpy.types.NodeTree,
                 node_type: str):
    normal_map = material_node_tree.nodes.new(node_type)
    normal_map.location.x -= loc_x
    normal_map.location.y += loc_y
    return normal_map


def get_texture_ext(texture_exc: str):
    if texture_exc == '':
        print("No texture extension to replace blp with set in addon preferences")
        texture_exc = 'png'
    if texture_exc[0] != '.':
        texture_exc = '.' + texture_exc
    return texture_exc


def get_image(folders: List[str],
              team_color: str,
              texture: War3Texture,
              texture_exc: str):
    image_file = get_image_file(team_color, texture, texture_exc)
    print("loading:", image_file)
    file_path_parts = image_file.split(os.path.sep)

    file_name = file_path_parts[-1].split('.')[0]
    bpy_image = bpy.data.images.new(file_name, 0, 0)
    bpy_image.source = 'FILE'

    bpy_image.filepath = find_file(file_path_parts, folders, image_file)
    return bpy_image


def get_image_file(team_color: str,
                   texture: War3Texture,
                   texture_exc: str) -> str:
    if texture.replaceable_id == 1:  # Team Color
        image_file = constants.TEAM_COLOR_IMAGES[team_color]
    elif texture.replaceable_id == 2:  # Team Glow
        image_file = constants.TEAM_GLOW_IMAGES[team_color]
    else:
        image_file = texture.texture_path
    if image_file.endswith(".blp"):
        image_file = image_file.split(".blp")[0] + texture_exc
    image_file = image_file.replace("/", os.path.sep)
    image_file = image_file.replace("\\", os.path.sep)
    return image_file


def find_file(file_path_parts: List[str],
              folders: List[str],
              image_file: str) -> str:
    for i in range(len(file_path_parts)):
        split = image_file.split(os.path.sep, i)
        image_file = split[len(split) - 1]

        for folder in folders:
            file_path = check_file_path(folder, image_file)
            if 0 < len(file_path):
                return file_path
    return ''


def get_folders(alt_folder: str,
                resource_folder: str,
                model_file: str) -> List[str]:
    if resource_folder == '':
        print("No resource folder set in addon preferences")

    elif not resource_folder.endswith(os.path.sep):
        # elif not resource_folder.endswith("\\"):
        resource_folder += os.path.sep
    if alt_folder == '':
        print("No alt resource folder set in addon preferences")
    elif not alt_folder.endswith(os.path.sep):
        alt_folder += os.path.sep

    model_folder = str(Path(model_file).parent)
    if not model_folder.endswith(os.path.sep):
        model_folder += os.path.sep
    # print("model folder:", model_folder)
    textures1 = "Textures" + os.path.sep
    textures2 = "textures" + os.path.sep
    folders1 = [model_folder,
                model_folder + textures1, model_folder + textures2,
                resource_folder, alt_folder,
                resource_folder + textures1, resource_folder + textures2,
                alt_folder + textures1, alt_folder + textures2]
    folders = []
    for folder in folders1:
        f = check_file_path(folder, "")
        if f != '' and f not in folders:
            folders.append(f)
    return folders


def check_file_path(folder: str, image_file: str) -> str:
    file_path = folder + image_file
    try:
        if Path(file_path).exists():
            return file_path
    except OSError:
        print("bad path:", file_path)
    return ''
