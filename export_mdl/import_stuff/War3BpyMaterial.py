from typing import Optional

import bpy


class War3BpyMaterial:
    def __init__(self, material_name: str):
        self.material_name: str = material_name
        self.bpy_material: bpy.types.Material = self.get_new_material(material_name)
        self.material_node_tree = self.bpy_material.node_tree
        self.shader_node: bpy.types.Node = self.get_shader_node()
        self.node_width: float = self.shader_node.width

    def get_new_material(self, material_name: str):
        bpy_material: bpy.types.Material = bpy.data.materials.new(name=material_name)
        bpy_material.shadow_method = 'NONE'
        bpy_material.use_nodes = True
        bpy_material.blend_method = 'HASHED'
        bpy_material.shadow_method = 'HASHED'
        bpy_material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
        return bpy_material

    def get_shader_node(self):
        shader_node = self.find_shader_node()
        if shader_node is None:
            shader_node = self.get_new_node(0, 1, "ShaderNodeBsdfPrincipled")
        if shader_node.inputs.get("Specular"):
            shader_node.inputs.get("Specular").default_value = 0.0  # no specular
        elif shader_node.inputs.get("Specular IOR Level"):
            shader_node.inputs.get("Specular IOR Level").default_value = 0.0  # no specular
        if shader_node.inputs.get("Roughness"):
            shader_node.inputs.get("Roughness").default_value = 1.0  # full roughness
        return shader_node

    def find_shader_node(self) -> Optional[bpy.types.Node]:
        for node in self.material_node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
                return node
        return None

    def get_mix_node(self):
        mix_node = self.get_new_node(0, 1, "ShaderNodeMixRGB")
        mix_node.blend_type = 'MULTIPLY'
        mix_node.inputs[0].default_value = 1.0
        self.connect(mix_node.outputs.get("Color"), self.shader_node.inputs.get("Base Color"))
        return mix_node

    def get_geoset_anim_color_node(self, mix_node):
        geo_color_node = self.get_new_node(1, 1, "ShaderNode")
        geo_color_node.outputs[0].default_value = (1, 1, 1, 1)
        geo_color_node.name = 'Geoset Anim Color'
        geo_color_node.label = 'Geoset Anim Color'
        self.connect(geo_color_node.outputs.get("Result"), mix_node.inputs.get("A"))
        return geo_color_node

    def get_geoset_anim_alpha_node(self):
        geo_alpha_node = self.get_new_node(0, 4, "ShaderNodeMath")
        geo_alpha_node.inputs[0].default_value = 1.0
        geo_alpha_node.inputs[1].default_value = 1.0
        geo_alpha_node.operation = 'MULTIPLY'
        geo_alpha_node.use_clamp = True
        geo_alpha_node.name = 'Geoset Anim Alpha'
        geo_alpha_node.label = 'Geoset Anim Alpha'
        self.connect(geo_alpha_node.outputs[0], self.get_input("Alpha"))
        return geo_alpha_node

    def get_new_node(self, grid_x: float,
                     grid_y: float,
                     node_type: str):
        new_node = self.material_node_tree.nodes.new(node_type)
        new_node.location.x -= ((1+grid_x) * self.node_width)
        new_node.location.y += ((2-grid_y) * 200)
        return new_node

    def connect(self, node_output: bpy.types.NodeSocket, node_input: bpy.types.NodeSocket):
        self.material_node_tree.links.new(node_output, node_input)

    def get_input(self, input_name: str):
        return self.shader_node.inputs.get(input_name)

    def get_path(self):
        return 'bpy.data.materials["{0}"]'.format(self.material_name)

    def get_geo_color_path(self):
        return self.get_path() + '.node_tree.nodes["Geoset Anim Color"].outputs[0].default_value'

    def get_geo_alpha_path(self):
        return self.get_path() + '.node_tree.nodes["Geoset Anim Alpha"].inputs[1].default_value'

