# Viewport preview of geoset animations: the object's color follows its Warcraft 3 geoset alpha and color
# through drivers, and its materials multiply in Object Info, so fades and tints show in Material Preview per
# object (even when objects share a material). Nothing here is read by the exporter.
import bpy

PREVIEW_ALPHA_NODE = "Geoset Preview Alpha"
PREVIEW_COLOR_NODE = "Geoset Preview Color"


def add_color_drivers(obj: bpy.types.Object):
    """Drive obj.color (RGBA) from obj.mdl_geoset (color, alpha). Plain variable drivers, no Python needed."""
    for index in range(4):
        try:
            obj.driver_remove("color", index)
        except TypeError:
            pass
        fcurve = obj.driver_add("color", index)
        driver = fcurve.driver
        driver.type = 'AVERAGE'
        var = driver.variables.new()
        var.name = "v"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = obj
        var.targets[0].data_path = "mdl_geoset.alpha" if index == 3 else "mdl_geoset.color[%d]" % index


def _shader(tree: bpy.types.NodeTree):
    return next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)


def add_material_preview(material: bpy.types.Material):
    """Multiply Object Info alpha into the shader's Alpha and Object Info color into its Base Color, once."""
    if material is None or not material.use_nodes or material.node_tree is None:
        return
    tree = material.node_tree
    shader = _shader(tree)
    if shader is None or tree.nodes.get(PREVIEW_ALPHA_NODE) is not None:
        return
    info = tree.nodes.new('ShaderNodeObjectInfo')
    info.location = (shader.location.x - 250, shader.location.y + 300)

    alpha_input = shader.inputs['Alpha']
    alpha_mul = tree.nodes.new('ShaderNodeMath')
    alpha_mul.name = alpha_mul.label = PREVIEW_ALPHA_NODE
    alpha_mul.operation = 'MULTIPLY'
    alpha_mul.location = (shader.location.x - 200, shader.location.y - 450)
    if alpha_input.links:
        tree.links.new(alpha_input.links[0].from_socket, alpha_mul.inputs[0])
    else:
        alpha_mul.inputs[0].default_value = alpha_input.default_value
    tree.links.new(info.outputs['Alpha'], alpha_mul.inputs[1])
    tree.links.new(alpha_mul.outputs[0], alpha_input)

    color_input = shader.inputs['Base Color']
    color_mul = tree.nodes.new('ShaderNodeVectorMath')
    color_mul.name = color_mul.label = PREVIEW_COLOR_NODE
    color_mul.operation = 'MULTIPLY'
    color_mul.location = (shader.location.x - 200, shader.location.y + 150)
    if color_input.links:
        tree.links.new(color_input.links[0].from_socket, color_mul.inputs[0])
    else:
        color_mul.inputs[0].default_value = tuple(color_input.default_value)[:3]
    tree.links.new(info.outputs['Color'], color_mul.inputs[1])
    tree.links.new(color_mul.outputs[0], color_input)

    if hasattr(material, "blend_method") and material.blend_method == 'OPAQUE':
        material.blend_method = 'HASHED'  # EEVEE Legacy needs this to show alpha


def add_geoset_preview(obj: bpy.types.Object):
    add_color_drivers(obj)
    for slot in obj.material_slots:
        add_material_preview(slot.material)
