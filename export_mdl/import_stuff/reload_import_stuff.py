import importlib
from .mdl_parser import reload_mdl_parser
from .mdx_parser import reload_mdx_parser
from . import create_armature_actions
from . import create_armature_object
from . import create_material
from . import create_mesh_objects
from . import create_object_actions
from . import create_other_objects
from . import load_stuff
from . import load_warcraft_3_model
from . import MDXImportProperties
from . import War3BpyMaterial

try:
    print("    reloading import modules")
    importlib.reload(reload_mdl_parser)
    importlib.reload(reload_mdx_parser)
    importlib.reload(create_armature_actions)
    importlib.reload(create_armature_object)
    importlib.reload(create_material)
    importlib.reload(create_mesh_objects)
    importlib.reload(create_object_actions)
    importlib.reload(create_other_objects)
    importlib.reload(load_stuff)
    importlib.reload(load_warcraft_3_model)
    importlib.reload(MDXImportProperties)
    importlib.reload(War3BpyMaterial)
except ImportError:
    print("    could not reload import modules")
