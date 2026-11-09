# An HD material's layer list is its six texture slots. They're filled as soon as the material is made HD, with
# the node tree's images where it has them and the textures Blizzard's own HD materials bind otherwise.
import bpy

HD_SLOT_NAMES = ("Diffuse", "Normal", "ORM", "Emissive", "Team Color", "Environment")

# (texture type, path) per slot; texture type '1' is the team color (replaceable id 1)
HD_SLOT_DEFAULTS = (
    ('0', "Textures\\white.blp"),
    ('0', "Textures\\normal.blp"),
    ('0', "Textures\\orm.blp"),
    ('0', "Textures\\black32.blp"),
    ('1', ""),
    ('0', "ReplaceableTextures\\EnvironmentMap.blp"),
)


def is_hd(material: bpy.types.Material) -> bool:
    return getattr(material, "mdl_shader", 'AUTO') in ('HD', 'CRYSTAL')


def set_slot(item, slot: int, path: str = None):
    """Point a layer at a slot's texture: the given path, or the slot's default."""
    texture_type, default = HD_SLOT_DEFAULTS[slot]
    item.name = HD_SLOT_NAMES[slot]
    item.texture_type = texture_type if path is None else '0'
    item.path = default if path is None else path


def is_default(item, slot: int) -> bool:
    texture_type, default = HD_SLOT_DEFAULTS[slot]
    if item.texture_type != texture_type:
        return False
    return texture_type != '0' or item.path.replace('/', '\\').lower() == default.lower()


def node_paths(material: bpy.types.Material):
    """The images the node tree feeds into each slot (None where it has none), the way the exporter reads them."""
    from .classes.model_utils.create_material_stuff import layers_from_mat_nodes, HD_DEFAULT_TEXTURES
    paths = [None] * len(HD_SLOT_NAMES)
    layers = layers_from_mat_nodes(material, True) or []
    for slot, layer in enumerate(layers[:len(paths)]):
        path = getattr(layer, "texture_path", None)
        if path and path != HD_DEFAULT_TEXTURES[slot] and not path.startswith("ReplaceableId"):
            paths[slot] = path
    return paths


def fill_hd_slots(material: bpy.types.Material) -> int:
    """Add the slots the layer list is missing. Existing layers stay where they are. Returns how many were added."""
    layers = material.mdl_layers
    start = len(layers)
    if start >= len(HD_SLOT_NAMES):
        return 0
    paths = node_paths(material) if start == 0 else [None] * len(HD_SLOT_NAMES)
    for slot in range(start, len(HD_SLOT_NAMES)):
        set_slot(layers.add(), slot, paths[slot])
    if start == 0:
        material.mdl_layer_index = 0
    return len(HD_SLOT_NAMES) - start


def shader_changed(material, context):
    if is_hd(material):
        fill_hd_slots(material)
