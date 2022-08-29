import importlib
from . import transform_rot
from . import transform_vec

try:
    print("    reloading transform modules")
    importlib.reload(transform_rot)
    importlib.reload(transform_vec)
except ImportError:
    print("    could not reload transform modules")
