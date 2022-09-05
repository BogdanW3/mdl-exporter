import importlib
from . import get_wc3_animation_curve
from . import space_actions
from . import split_segment
from . import transform_rot
from . import transform_vec


try:
    print("    reloading animUtils modules")
    importlib.reload(get_wc3_animation_curve)
    importlib.reload(space_actions)
    importlib.reload(split_segment)
    importlib.reload(transform_rot)
    importlib.reload(transform_vec)
except ImportError:
    print("    could not reload animUtils modules")
