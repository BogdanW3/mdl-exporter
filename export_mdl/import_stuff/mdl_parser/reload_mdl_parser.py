import importlib
from . import get_vertex_groups
from . import load_mdl
from . import mdl_parser_reload
from . import mdl_reader
from . import parse_attachments
from . import parse_bones
from . import parse_collision_shapes
from . import parse_events
from . import parse_geometry
from . import parse_geoset_animations
from . import parse_geoset_color
from . import parse_geoset_transformation
from . import parse_geosets
from . import parse_helpers
from . import parse_light
from . import parse_materials
from . import parse_mdl
from . import parse_model
from . import parse_node
from . import parse_pivot_points
from . import parse_sequences
from . import parse_textures
from . import parse_version

try:
    print("    reloading mdl import modules")
    importlib.reload(get_vertex_groups)
    importlib.reload(load_mdl)
    importlib.reload(mdl_parser_reload)
    importlib.reload(mdl_reader)
    importlib.reload(parse_attachments)
    importlib.reload(parse_bones)
    importlib.reload(parse_collision_shapes)
    importlib.reload(parse_events)
    importlib.reload(parse_geometry)
    importlib.reload(parse_geoset_animations)
    importlib.reload(parse_geoset_color)
    importlib.reload(parse_geoset_transformation)
    importlib.reload(parse_geosets)
    importlib.reload(parse_helpers)
    importlib.reload(parse_light)
    importlib.reload(parse_materials)
    importlib.reload(parse_mdl)
    importlib.reload(parse_model)
    importlib.reload(parse_node)
    importlib.reload(parse_pivot_points)
    importlib.reload(parse_sequences)
    importlib.reload(parse_textures)
    importlib.reload(parse_version)
except ImportError:
    print("    could not reload mdl import modules")
