# Viewport preview of geoset animations: materials read each object's Warcraft 3 geoset alpha and color through
# Attribute nodes (Object mode reads a property path from the object being drawn), so fades and tints show in
# Material Preview and renders per object, even when objects share a material. Nothing here is exported.
import bpy

PREVIEW_ALPHA_NODE = "Geoset Preview Alpha"
PREVIEW_COLOR_NODE = "Geoset Preview Color"


def _shader(tree: bpy.types.NodeTree):
    return next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)


def _object_attribute(tree: bpy.types.NodeTree, path: str, location):
    node = tree.nodes.new('ShaderNodeAttribute')
    node.attribute_type = 'OBJECT'
    node.attribute_name = path
    node.location = location
    return node


def has_material_preview(material: bpy.types.Material) -> bool:
    return material is not None and material.node_tree is not None \
        and material.node_tree.nodes.get(PREVIEW_ALPHA_NODE) is not None


def add_material_preview(material: bpy.types.Material):
    """Multiply the object's geoset alpha into the shader's Alpha and its geoset color into Base Color, once."""
    if material is None or not material.use_nodes or material.node_tree is None or has_material_preview(material):
        return
    tree = material.node_tree
    shader = _shader(tree)
    if shader is None:
        return
    x, y = shader.location.x, shader.location.y

    alpha_input = shader.inputs['Alpha']
    alpha_attr = _object_attribute(tree, "mdl_geoset.alpha", (x - 450, y - 450))
    alpha_mul = tree.nodes.new('ShaderNodeMath')
    alpha_mul.name = alpha_mul.label = PREVIEW_ALPHA_NODE
    alpha_mul.operation = 'MULTIPLY'
    alpha_mul.location = (x - 200, y - 450)
    if alpha_input.links:
        tree.links.new(alpha_input.links[0].from_socket, alpha_mul.inputs[0])
    else:
        alpha_mul.inputs[0].default_value = alpha_input.default_value
    tree.links.new(alpha_attr.outputs['Fac'], alpha_mul.inputs[1])
    tree.links.new(alpha_mul.outputs[0], alpha_input)

    color_input = shader.inputs['Base Color']
    color_attr = _object_attribute(tree, "mdl_geoset.color", (x - 450, y + 150))
    color_mul = tree.nodes.new('ShaderNodeVectorMath')
    color_mul.name = color_mul.label = PREVIEW_COLOR_NODE
    color_mul.operation = 'MULTIPLY'
    color_mul.location = (x - 200, y + 150)
    if color_input.links:
        tree.links.new(color_input.links[0].from_socket, color_mul.inputs[0])
    else:
        color_mul.inputs[0].default_value = tuple(color_input.default_value)[:3]
    tree.links.new(color_attr.outputs['Color'], color_mul.inputs[1])
    tree.links.new(color_mul.outputs[0], color_input)

    if hasattr(material, "blend_method") and material.blend_method == 'OPAQUE':
        material.blend_method = 'HASHED'  # EEVEE Legacy needs this to show alpha


def has_geoset_preview(obj: bpy.types.Object) -> bool:
    materials = [slot.material for slot in obj.material_slots if slot.material is not None]
    return bool(materials) and all(has_material_preview(m) for m in materials)


def add_geoset_preview(obj: bpy.types.Object):
    for slot in obj.material_slots:
        add_material_preview(slot.material)
