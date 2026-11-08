import re
from typing import Optional, List

from .parse_node import parse_node
from ...classes.War3Light import War3Light

LIGHT_TYPES = ('Omnidirectional', 'Directional', 'Ambient')


def parse_light(data: str) -> War3Light:
    light = War3Light("")
    parse_node(data, light)

    for light_type in LIGHT_TYPES:
        if re.search(r'\b%s\s*,' % light_type, data):
            light.light_type = light_type
            break

    # Only static values are read, animated ones keep their defaults
    light.atten_start = get_static_float(data, "AttenuationStart")
    light.atten_end = get_static_float(data, "AttenuationEnd")
    light.intensity = get_static_float(data, "Intensity")
    light.amb_intensity = get_static_float(data, "AmbIntensity")
    light.color = get_static_color(data, "Color")
    light.amb_color = get_static_color(data, "AmbColor")
    light.shadow_intensity = get_static_float(data, "ShadowIntensity")
    light.shadow_casting = re.search(r'\bShadowCasting\s*,', data) is not None
    for attr, name in (('shadow_casting_start', "ShadowCastingStart"), ('shadow_casting_end', "ShadowCastingEnd"),
                       ('quadratic_falloff', "QuadraticFalloff"), ('linear_falloff', "LinearFalloff"),
                       ('damping', "Damping")):
        value = get_static_float(data, name)
        if value is not None:
            setattr(light, attr, value)

    return light


def get_static_float(data: str, name: str) -> Optional[float]:
    match = re.search(r'static\s+%s\s+([-+0-9.eE]+)' % name, data)
    return float(match.group(1)) if match else None


def get_static_color(data: str, name: str) -> Optional[List[float]]:
    match = re.search(r'static\s+%s\s*\{([^}]*)\}' % name, data)
    if match is None:
        return None
    # MDL colors are stored as BGR
    return [float(v) for v in match.group(1).split(',') if v.strip()][2::-1]
