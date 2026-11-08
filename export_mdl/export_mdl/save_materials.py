from typing import TextIO, Set, List

from .write_animation_chunk import write_animation_chunk
from .. import constants
from ..classes.War3Layer import War3Layer
from ..classes.War3Material import War3Material
from ..classes.War3Texture import War3Texture
from ..classes.War3TextureAnim import War3TextureAnim
from ..utils import float2str


def save_materials(fw: TextIO.write,
                   materials: List[War3Material],
                   textures: List[War3Texture],
                   tvertex_anims: List[War3TextureAnim],
                   global_seqs: Set[int],
                   version: int = 800):
    if len(materials):
        fw("Materials %d {\n" % len(materials))
        for material in materials:
            fw("\tMaterial {\n")

            # HD materials only exist from v900 on, older versions get the layers as plain SD layers
            hd = 900 <= version and material.layers[0].hd
            shader_name = constants.SHADER_NAMES.get(material.layers[0].shader or 1)

            if material.use_const_color is True:
                fw("\t\tConstantColor,\n")

            # SortPrimsFarZ,
            # FullResolution,

            if material.priority_plane != 0:
                fw("\t\tPriorityPlane %d,\n" % material.priority_plane)

            if hd and version < 1100:
                # v900/v1000 name the shader once per material, v1100+ per layer
                fw("\t\tShader \"%s\",\n" % shader_name)

            if hd:
                # In MDL text every PBR texture goes in one layer, bound to its slot. Only binary v900/v1000
                # spreads them over one layer each.
                layer_shader = shader_name if 1100 <= version else None
                write_layer(fw, material.layers[0], material.layers, textures, tvertex_anims, global_seqs, True, layer_shader)
            else:
                for layer in material.layers:
                    write_layer(fw, layer, [layer], textures, tvertex_anims, global_seqs, False, None)
            fw("\t}\n")
        fw("}\n")


def write_layer(fw: TextIO.write,
                layer: War3Layer,
                texture_layers: List[War3Layer],
                textures: List[War3Texture],
                tvertex_anims: List[War3TextureAnim],
                global_seqs: Set[int],
                with_slots: bool,
                shader_name):
    fw("\t\tLayer {\n")
    fw("\t\t\tFilterMode %s,\n" % layer.filter_mode)
    if layer.unshaded is True:
        fw("\t\t\tUnshaded,\n")

    if layer.wrap_width:
        fw("\t\t\tWrapWidth,\n")

    if layer.wrap_height:
        fw("\t\t\tWrapHeight,\n")

    if layer.sphere_env_map:
        fw("\t\t\tSphereEnvMap,\n")

    if layer.two_sided is True:
        fw("\t\t\tTwoSided,\n")

    if layer.unfogged is True:
        fw("\t\t\tUnfogged,\n")

    if layer.no_depth_test:
        fw("\t\t\tNoDepthTest,\n")

    if layer.no_depth_set:
        fw("\t\t\tNoDepthSet,\n")

    if layer.unlit:
        fw("\t\t\tUnlit,\n")

    if layer.back_faces_for_shadows:
        fw("\t\t\tBackFacesForShadows,\n")

    if layer.ambient_occlusion:
        fw("\t\t\tAmbientOcclusion,\n")

    if shader_name is not None:
        fw("\t\t\tShader \"%s\",\n" % shader_name)

    for slot, texture_layer in enumerate(texture_layers):
        texture_id = textures.index(texture_layer.texture) if texture_layer.texture is not None else 0
        if with_slots:
            fw("\t\t\tstatic TextureID %d <= %d,\n" % (texture_id, slot))
        else:
            fw("\t\t\tstatic TextureID %d,\n" % texture_id)

    if layer.texture_anim is not None:
        fw("\t\t\tTVertexAnimId %d,\n" % tvertex_anims.index(layer.texture_anim))

    if layer.alpha_anim is not None:
        write_animation_chunk(fw, layer.alpha_anim, "Alpha", global_seqs, "\t\t")
    else:
        fw("\t\t\tstatic Alpha %s,\n" % float2str(layer.alpha_value))

    fw("\t\t}\n")
