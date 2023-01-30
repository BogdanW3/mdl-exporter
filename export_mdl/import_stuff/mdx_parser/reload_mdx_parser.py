import importlib
from . import get_vertex_groups
from . import load_mdx
from . import parse_alpha
from . import parse_attachment
from . import parse_attachments
from . import parse_bones
from . import parse_collision_shapes
from . import parse_events
from . import parse_fresnel_color
from . import parse_geometry
from . import parse_geoset_animations
from . import parse_geoset_color
from . import parse_timeline
from . import parse_geosets
from . import parse_helpers
from . import parse_layers
from . import parse_lights
from . import parse_material_texture_id
from . import parse_materials
from . import parse_mdx
from . import parse_model
from . import parse_node
from . import parse_pivot_points
from . import parse_sequences
from . import parse_textures
from . import parse_tracks
from . import parse_version
from . import binary_reader
from . import parser_reload

try:
    print("    reloading mdx import modules")
    importlib.reload(get_vertex_groups)
    importlib.reload(load_mdx)
    importlib.reload(parse_alpha)
    importlib.reload(parse_attachment)
    importlib.reload(parse_attachments)
    importlib.reload(parse_bones)
    importlib.reload(parse_collision_shapes)
    importlib.reload(parse_events)
    importlib.reload(parse_fresnel_color)
    importlib.reload(parse_geometry)
    importlib.reload(parse_geoset_animations)
    importlib.reload(parse_geoset_color)
    importlib.reload(parse_timeline)
    importlib.reload(parse_geosets)
    importlib.reload(parse_helpers)
    importlib.reload(parse_layers)
    importlib.reload(parse_lights)
    importlib.reload(parse_material_texture_id)
    importlib.reload(parse_materials)
    importlib.reload(parse_mdx)
    importlib.reload(parse_model)
    importlib.reload(parse_node)
    importlib.reload(parse_pivot_points)
    importlib.reload(parse_sequences)
    importlib.reload(parse_textures)
    importlib.reload(parse_tracks)
    importlib.reload(parse_version)
    importlib.reload(binary_reader)
    importlib.reload(parser_reload)

except ImportError:
    print("    could not reload mdx import modules")
