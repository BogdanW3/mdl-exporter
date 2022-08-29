import importlib
from . import get_wc3_animation_curve
from . import space_actions
from . import split_segment

try:
    print("    reloading animUtils modules")
    importlib.reload(get_wc3_animation_curve)
    importlib.reload(space_actions)
    importlib.reload(split_segment)
except ImportError:
    print("    could not reload animUtils modules")
