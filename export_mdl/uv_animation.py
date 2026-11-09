# Texture animations (TXAN): a layer's UVs translated, rotated and scaled over time.
#
# In Blender one lives on a Mapping node that holds the file's own values (location = translation, rotation =
# the quaternion as Euler angles, scale = scaling), keyed on the material's node tree. Warcraft 3 UVs run top
# to bottom where Blender's run bottom to top, so the node sits between two fixed V flips: the viewport shows
# the animation the way the game applies it, and the keys export unchanged.
from typing import Iterable, List, Optional

import bpy
from mathutils import Euler

LOCATION, ROTATION, SCALE = 1, 2, 3  # Mapping node inputs (Blender 2.81+)
FLIP_LABEL = "Warcraft 3 UV flip"
ANIM_LABEL = "Warcraft 3 Texture Animation"


def socket_path(node: bpy.types.Node, index: int) -> str:
    return 'nodes["%s"].inputs[%d].default_value' % (bpy.utils.escape_identifier(node.name), index)


def _flip(nodes, location):
    node = nodes.new('ShaderNodeMapping')
    node.vector_type = 'POINT'
    node.inputs[LOCATION].default_value = (0.0, 1.0, 0.0)
    node.inputs[SCALE].default_value = (1.0, -1.0, 1.0)
    node.label = FLIP_LABEL
    node.location = location
    node.hide = True
    return node


def add_uv_animation(material: bpy.types.Material, image_nodes: Iterable[bpy.types.Node],
                     name: str = "UV Animation") -> bpy.types.Node:
    """Wire UV -> flip -> animation Mapping node -> flip -> each image node, and return the animation node."""
    tree = material.node_tree
    nodes = tree.nodes
    image_nodes = list(image_nodes)
    x = min((n.location.x for n in image_nodes), default=0.0) - 900
    y = max((n.location.y for n in image_nodes), default=0.0)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (x, y)
    flip_in = _flip(nodes, (x + 200, y))
    anim = nodes.new('ShaderNodeMapping')
    anim.vector_type = 'POINT'
    anim.name = name
    anim.label = ANIM_LABEL
    anim.location = (x + 400, y)
    flip_out = _flip(nodes, (x + 600, y))
    tree.links.new(coords.outputs['UV'], flip_in.inputs[0])
    tree.links.new(flip_in.outputs[0], anim.inputs[0])
    tree.links.new(anim.outputs[0], flip_out.inputs[0])
    for image in image_nodes:
        tree.links.new(flip_out.outputs[0], image.inputs['Vector'])
    ensure_tree_action(material)
    return anim


def ensure_tree_action(material: bpy.types.Material):
    """Give the node tree an action of its own. Blender 4.4/4.5 otherwise reuse the material's action for it (when
    the material has keys, e.g. a layer's alpha), and keys inserted from Python don't land."""
    from .action_compat import assign_action
    tree = material.node_tree
    if tree.animation_data is not None and tree.animation_data.action is not None:
        return
    action = bpy.data.actions.new(material.name + " Texture Animation")
    if hasattr(action, "id_root"):
        action.id_root = 'NODETREE'
    assign_action(tree, action)


def find_uv_node(material: bpy.types.Material, layer) -> Optional[bpy.types.Node]:
    """The Mapping node a layer's texture animation is read from: the one it names, or (older files) a node
    with the layer's own name."""
    if not material.use_nodes or material.node_tree is None:
        return None
    nodes = material.node_tree.nodes
    for name in (getattr(layer, "uv_node", ""), layer.name):
        node = nodes.get(name) if name else None
        if node is not None and node.bl_idname == 'ShaderNodeMapping':
            return node
    return None


def read_texture_anim(material: bpy.types.Material, node: bpy.types.Node, sequences, global_seqs):
    """A War3TextureAnim from the node's keys, or None when it isn't animated."""
    from .classes.War3TextureAnim import War3TextureAnim
    from .classes.animation_curve_utils.get_wc3_animation_curve import get_own_animation_curve
    tree = material.node_tree
    translation = get_own_animation_curve(tree, socket_path(node, LOCATION), 3, global_seqs, sequences,
                                          [0.0, 0.0, 0.0])
    rotation = get_own_animation_curve(tree, socket_path(node, ROTATION), 3, global_seqs, sequences,
                                       [0.0, 0.0, 0.0])
    scale = get_own_animation_curve(tree, socket_path(node, SCALE), 3, global_seqs, sequences, [1.0, 1.0, 1.0])
    if not any((translation, rotation, scale)):
        return None
    for curve, kind in ((translation, 'Translation'), (rotation, 'Rotation'), (scale, 'Scale')):
        if curve is not None:
            curve.type = kind
    if rotation is not None:
        # Euler angles to the quaternions the file holds. Rotation tangents don't carry over (they interpolate on
        # the sphere), as with bones.
        for frame, value in list(rotation.keyframes.items()):
            rotation.keyframes[frame] = list(Euler(value[:3]).to_quaternion())
        if rotation.interpolation in ('Bezier', 'Hermite'):
            rotation.interpolation = 'Linear'
        rotation.handles_left.clear()
        rotation.handles_right.clear()
    anim = War3TextureAnim()
    anim.set_from(translation, rotation, scale)
    return anim


def compatible_eulers(quaternions: List) -> List[Euler]:
    """Euler angles for a run of quaternions (w, x, y, z), each close to the one before."""
    from mathutils import Quaternion
    eulers = []
    previous = None
    for value in quaternions:
        euler = Quaternion(value).to_euler('XYZ', previous) if previous is not None \
            else Quaternion(value).to_euler('XYZ')
        eulers.append(euler)
        previous = euler
    return eulers
