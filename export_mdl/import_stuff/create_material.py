import os
import re
from pathlib import Path
from typing import List, Dict

import bpy

from export_mdl import constants
from export_mdl.classes.War3Material import War3Material
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Texture import War3Texture
from export_mdl.import_stuff.War3BpyMaterial import War3BpyMaterial
from export_mdl.properties.War3Preferences import War3Preferences


def create_material(model: War3Model, team_color: str) -> Dict[str, War3BpyMaterial]:
    bpy_images = load_and_get_textures(model, team_color)

    print(" creating materials")
    bpy_materials: Dict[str, War3BpyMaterial] = {}
    for i, material in enumerate(model.materials):
        print("  material #" + str(i), material.name)
        images: List[bpy.types.Image] = []
        for layer in material.layers:
            images.append(bpy_images[layer.texture.texture_path])

        bpy_material = create_bpy_material(images, layer.hd, team_color)

        bpy_materials[str(i)] = bpy_material

    return bpy_materials


def create_bpy_material(images: List[bpy.types.Image], hd: bool, team_color: str):
    material_name = images[0].filepath.split(os.path.sep)[-1].split('.')[0]
    war3_bpy_material = War3BpyMaterial(material_name)

    tc_mix = war3_bpy_material.get_new_node(1, 0, 'ShaderNodeMix')
    tc_mix.blend_type = 'MULTIPLY'
    tc_mix.data_type = 'RGBA'
    tc_mix.inputs[0].default_value = 1.0
        
    war3_bpy_material.connect(tc_mix.outputs.get("Result"), war3_bpy_material.get_input("Base Color"))
    if hd:

        for i, bpy_image in enumerate(images):
            if i < 4: # don't create image nodes for the textures we don't use
                texture_mat_node = war3_bpy_material.get_new_node(3, i, 'ShaderNodeTexImage')
                texture_mat_node.image = bpy_image
            if i == 0:
                war3_bpy_material.connect(texture_mat_node.outputs.get("Color"), tc_mix.inputs.get("A"))
                war3_bpy_material.connect(texture_mat_node.outputs.get("Alpha"), war3_bpy_material.get_input("Alpha"))
            elif i == 1:
                texture_mat_node.image.colorspace_settings.is_data = True
                normal_map_node = war3_bpy_material.get_new_node(1, i, 'ShaderNodeNormalMap')

                # Blender 3.x added support for dds normal maps, we don't need to do anything special anymore
                war3_bpy_material.connect(texture_mat_node.outputs.get("Color"), normal_map_node.inputs.get("Color"))

                war3_bpy_material.connect(normal_map_node.outputs.get("Normal"), war3_bpy_material.get_input("Normal"))
            elif i == 2:
                orm = war3_bpy_material.get_new_node(1, i, 'ShaderNodeSeparateRGB')

                war3_bpy_material.connect(texture_mat_node.outputs.get("Color"), orm.inputs.get("Image"))

                war3_bpy_material.connect(orm.outputs.get("G"), war3_bpy_material.get_input("Roughness"))
                war3_bpy_material.connect(orm.outputs.get("B"), war3_bpy_material.get_input("Metallic"))
                war3_bpy_material.connect(texture_mat_node.outputs.get("Alpha"), tc_mix.inputs.get("Factor"))
            elif i == 3:
                emSlot = war3_bpy_material.get_input("Emission")
                if emSlot is None:
                    emSlot = war3_bpy_material.get_input("Emission Color")
                war3_bpy_material.connect(texture_mat_node.outputs.get("Color"), emSlot)
            elif i == 4:
                color_wheel = war3_bpy_material.get_new_node(3, -1, 'ShaderNodeRGB')
                color_wheel.outputs[0].default_value = (*constants.TEAM_COLORS[int(team_color)], 1.0)

                war3_bpy_material.connect(color_wheel.outputs.get("Color"), tc_mix.inputs.get("B"))
                pass
            elif i == 5:
                # skip the environmental map, possibly change the world's map to it
                pass
            else:
                print("Unknown texture slot", i, " in ", material_name)
            print(bpy_image.filepath, " at place ", i)
    else:
        next_color_input = tc_mix.inputs.get("B")
        next_alpha_input = war3_bpy_material.get_geoset_anim_alpha_node().inputs[0]
        for i, bpy_image in enumerate(images):
            texture_mat_node = war3_bpy_material.get_new_node(i*2+3, i, 'ShaderNodeTexImage')
            texture_mat_node.image = bpy_image
            mix_node = war3_bpy_material.get_new_node(i*2+1.5, i, "ShaderNodeMix")
            mix_node.blend_type = 'MULTIPLY' # shouldn't always be multiply...
            mix_node.data_type = 'RGBA'
            mix_node.inputs[0].default_value = 1.0
            mix_node.inputs.get("A").default_value = (1, 1, 1, 1)
            war3_bpy_material.connect(texture_mat_node.outputs.get("Color"), mix_node.inputs.get("B"))
            war3_bpy_material.connect(texture_mat_node.outputs.get("Alpha"), mix_node.inputs[0])
            war3_bpy_material.connect(mix_node.outputs.get("Result"), next_color_input)
            next_color_input = mix_node.inputs.get("B")

            alpha_node = war3_bpy_material.get_new_node(i*2+1, 4, "ShaderNodeMath")
            alpha_node.inputs[1].default_value = 0.0
            alpha_node.use_clamp = True
            war3_bpy_material.connect(texture_mat_node.outputs.get("Alpha"), alpha_node.inputs[0])
            war3_bpy_material.connect(alpha_node.outputs[0], next_alpha_input)
            next_alpha_input = alpha_node.inputs[1]
    return war3_bpy_material


def get_wc3_base_node(material_name: str):
    bpy_material: bpy.types.Material = bpy.data.materials.new(name=material_name)
    bpy_material.shadow_method = 'NONE'
    bpy_material.use_nodes = True

    bpy_material.blend_method = 'HASHED'
    bpy_material.shadow_method = 'HASHED'

    bpy_material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    texture_slot_index = 0
    material_node_tree = bpy_material.node_tree
    shader_node: bpy.types.Node = material_node_tree.nodes.get("Principled BSDF")
    shader_node.inputs[5].default_value = 0.0  # no specular
    shader_node.inputs[7].default_value = 1.0  # full roughness


    node_width: float = shader_node.width
    color_input_socket = shader_node.inputs.get("Base Color")
    mix_node = get_new_node(node_width + 20, 0, material_node_tree, "ShaderNodeMixRGB")
    mix_node.blend_type = 'MULTIPLY'
    mix_node.inputs[0].default_value = 1.0
    color_node = get_new_node(node_width + 200, 0, material_node_tree, "ShaderNodeRGB")
    color_node.outputs[0].default_value = (1, 1, 1, 1)
    color_node.name = 'Geoset Anim Color'
    material_node_tree.links.new(color_node.outputs.get("Color"), mix_node.inputs.get("Color1"))
    material_node_tree.links.new(color_node.outputs.get("Color"), mix_node.inputs.get("Color1"))
    material_node_tree.links.new(mix_node.outputs.get("Color"), shader_node.inputs.get("Base Color"))

    diffuse = material_node_tree.nodes.new('ShaderNodeMixRGB')
    diffuse.location.x -= node_width + 50
    diffuse.blend_type = 'COLOR'


def get_new_node(loc_x: float, loc_y: float, material_node_tree: bpy.types.NodeTree, node_type: str):
    new_node = material_node_tree.nodes.new(node_type)
    new_node.location.x -= loc_x
    new_node.location.y += loc_y
    return new_node


def load_and_get_textures(model: War3Model, team_color: str):
    print(" loading textures")
    preferences: War3Preferences = bpy.context.preferences.addons.get('export_mdl').preferences
    folders = get_folders(preferences.alternativeResourceFolder, preferences.resourceFolder, model.file)
    texture_ext = get_texture_ext(preferences.textureExtension)
    bpy_images: Dict[str, bpy.types.Image] = {}
    for texture in model.textures:
        if texture.texture_path not in bpy_images:
            image_file = get_image_file(team_color, texture, texture_ext)
            bpy_image = get_image(folders, image_file)
            bpy_images[texture.texture_path] = bpy_image
    return bpy_images


def get_texture_ext(texture_ext: str):
    if texture_ext == '':
        print("   No texture extension to replace blp with set in addon preferences")
        texture_ext = 'png'
    if texture_ext[0] != '.':
        texture_ext = '.' + texture_ext
    return texture_ext


def get_image(folders: List[Path], image_file: str,):
    print("  loading:", image_file)
    file_path_parts = image_file.split(os.path.sep)

    file_name = file_path_parts[-1].split('.')[0]
    bpy_image = bpy.data.images.new(file_name, 0, 0)
    bpy_image.source = 'FILE'

    bpy_image.filepath = find_file(file_path_parts, folders)
    return bpy_image


def get_image_file(team_color: str, texture: War3Texture, texture_ext: str) -> str:
    if texture.replaceable_id <= 0:
        image_file = texture.texture_path
    else:
        image_file = get_repl_img(texture.replaceable_id, team_color)

    sub = re.sub("\\.blp$", texture_ext, image_file)
    sub = re.sub("\\.tif$", texture_ext, sub)
    return re.sub("[/\\\\]", re.escape(os.path.sep), sub)


def get_repl_img(repl_id: int, team_color: str):
    if repl_id == 1:
        return constants.get_team_color(team_color)
    elif repl_id == 2:
        return constants.get_team_glow(team_color)
    else:
        return 'ReplaceableTextures\\AshenvaleTree\\AshenCanopyTree.blp'
    # match repl_id:
    #     case 1:
    #         return constants.TEAM_COLOR_IMAGES[team_color]
    #     case 2:
    #         return constants.TEAM_GLOW_IMAGES[team_color]
    #     case _:
    #         return 'ReplaceableTextures\\AshenvaleTree\\AshenCanopyTree.blp'


def find_file(image_path_comps: List[str], folders: List[Path]) -> str:
    image_file = image_path_comps[-1]
    sub_folders = image_path_comps[0:-1]
    sub_folders.append('')
    for i in range(len(image_path_comps)):
        sub_folder1 = '/'.join(image_path_comps[i:-1])
        sub_folder2 = '/'.join(image_path_comps[0:-i])

        for folder in folders:
            file_path = folder / sub_folder1 / image_file
            if is_valid_path(file_path):
                return str(file_path)
            file_path = folder / sub_folder2 / image_file
            if is_valid_path(file_path):
                return str(file_path)
    return ''


def get_folders(alt_folder: str, resource_folder: str, model_file: str) -> List[Path]:
    folders = []
    if resource_folder == '':
        print("    No resource folder set in addon preferences")
    if alt_folder == '':
        print("    No alt resource folder set in addon preferences")
    folders.extend(get_valid_folders(Path(model_file).parent))
    if resource_folder != '':
        folders.extend(get_valid_folders(Path(resource_folder)))
    if alt_folder != '':
        folders.extend(get_valid_folders(Path(alt_folder)))

    return folders


def get_valid_folders(folder_path: Path):
    paths = []
    if folder_path.is_dir():
        paths.append(folder_path)
        sub1: Path = (folder_path / "Textures")
        sub2: Path = (folder_path / "textures")
        if sub1.is_dir():
            paths.append(sub1)
        if sub2.is_dir():
            paths.append(sub2)
    return paths


def is_valid_path(file_path: Path) -> bool:
    try:
        if Path(file_path).exists():
            return True
    except OSError:
        print("bad path:", file_path)
    return False
