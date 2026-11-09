from typing import Dict, Optional

import bpy

# Principled BSDF inputs the exporter reads each HD texture slot from (see create_material_stuff.py)
SLOT_INPUTS = {
    'diffuse': ("Base Color",),
    'normal': ("Normal",),
    'orm': ("Roughness", "Metallic", "Specular"),
    'emissive': ("Emission Color", "Emission"),
}


def find_image(link: Optional[bpy.types.NodeLink], depth: int = 16) -> Optional[bpy.types.Image]:
    """The first image texture upstream of a link, through any nodes in between."""
    if link is None or depth <= 0:
        return None
    node = link.from_node
    if isinstance(node, bpy.types.ShaderNodeTexImage):
        return node.image
    for socket in node.inputs:
        for upstream in socket.links:
            image = find_image(upstream, depth - 1)
            if image is not None:
                return image
    return None


def current_images(material: bpy.types.Material) -> Dict[str, Optional[bpy.types.Image]]:
    found = {slot: None for slot in SLOT_INPUTS}
    tree = material.node_tree
    shader = next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if tree else None
    if shader is None:
        return found
    for slot, names in SLOT_INPUTS.items():
        for name in names:
            socket = shader.inputs.get(name)
            if socket is not None and socket.links:
                found[slot] = find_image(socket.links[0])
                if found[slot] is not None:
                    break
    return found


def build_hd_nodes(material: bpy.types.Material):
    """Rebuild the node tree into the layout the exporter reads for HD materials, keeping the images."""
    images = current_images(material)
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()

    output = tree.nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    shader = tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.location = (0, 0)
    tree.links.new(shader.outputs[0], output.inputs['Surface'])

    def image_node(slot: str, label: str, y: float, data: bool):
        node = tree.nodes.new('ShaderNodeTexImage')
        node.label = label
        node.location = (-700, y)
        node.image = images[slot]
        if data and node.image is not None:
            node.image.colorspace_settings.is_data = True
        return node

    diffuse = image_node('diffuse', "Diffuse", 300, False)
    tree.links.new(diffuse.outputs['Color'], shader.inputs['Base Color'])
    tree.links.new(diffuse.outputs['Alpha'], shader.inputs['Alpha'])

    normal = image_node('normal', "Normal", 0, True)
    normal_map = tree.nodes.new('ShaderNodeNormalMap')
    normal_map.location = (-300, 0)
    tree.links.new(normal.outputs['Color'], normal_map.inputs['Color'])
    tree.links.new(normal_map.outputs['Normal'], shader.inputs['Normal'])

    orm = image_node('orm', "ORM (occlusion, roughness, metallic)", -300, True)
    separate = tree.nodes.new('ShaderNodeSeparateColor')
    separate.location = (-300, -300)
    tree.links.new(orm.outputs['Color'], separate.inputs['Color'])
    tree.links.new(separate.outputs['Green'], shader.inputs['Roughness'])
    tree.links.new(separate.outputs['Blue'], shader.inputs['Metallic'])

    emissive = image_node('emissive', "Emissive", -600, False)
    emission = shader.inputs.get("Emission Color") or shader.inputs.get("Emission")
    tree.links.new(emissive.outputs['Color'], emission)
    strength = shader.inputs.get("Emission Strength")
    if strength is not None:
        strength.default_value = 1.0


class WAR3_OT_setup_hd_nodes(bpy.types.Operator):
    bl_idname = 'war_3.setup_hd_nodes'
    bl_label = 'Set Up HD Nodes'
    bl_description = ("Replace the material's node tree with one image node per HD texture slot (diffuse, normal, "
                      "ORM, emissive) wired the way the exporter reads them. Images already in the tree are kept")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        obj = context.active_object
        return obj is not None and obj.active_material is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: bpy.types.Context):
        material = context.active_object.active_material
        build_hd_nodes(material)
        if getattr(material, "mdl_shader", 'AUTO') not in ('HD', 'CRYSTAL'):
            material.mdl_shader = 'HD'
        self.report({'INFO'}, "Rebuilt %s as an HD material" % material.name)
        return {'FINISHED'}
