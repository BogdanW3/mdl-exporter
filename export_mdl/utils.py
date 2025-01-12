import math
from operator import itemgetter
from typing import SupportsRound, List, Tuple

decimal_places = 5


def rnd(val: float) -> float:
    return round(val, decimal_places)


def rnd(val: int) -> int:
    return round(val, decimal_places)


# def rnd(val: SupportsRound[_Protocol[T_co]]):
#     return round(val, decimal_places)


def float2str(value: float) -> str:
    return ('%.6f' % value).rstrip('0').rstrip('.')


def calc_bounds_radius(min_ext: List[float], max_ext: List[float]):
    x = (max_ext[0] - min_ext[0])/2
    y = (max_ext[1] - min_ext[1])/2
    z = (max_ext[2] - min_ext[2])/2
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))


def calc_extents(vertices: List[List[float]]) -> Tuple[List[float], List[float]]:
    # max_extents = [max(vertices, key=itemgetter(i))[i] for i in range(3)]
    # min_extents = [min(vertices, key=itemgetter(i))[i] for i in range(3)]

    min_extents: List[float] = [0.0, 0.0, 0.0]
    max_extents: List[float] = [0.0, 0.0, 0.0]

    for vertex in vertices:
        for i, v in enumerate(vertex):
            min_extents[i] = min(min_extents[i], v)
            max_extents[i] = max(max_extents[i], v)

    return min_extents, max_extents


def get_curve(obj, data_paths):
    if obj.animation_data and obj.animation_data.action:
        for path in data_paths:
            curve = obj.animation_data.action.fcurves.find(path)
            if curve is not None:
                return curve
    return None


def get_curves(obj, data_path, indices):
    curves = {}
    if obj.animation_data and obj.animation_data.action:
        for index in indices:
            curve = obj.animation_data.action.fcurves.find(data_path, index=index)
            if curve is not None:
                curves[(data_path.split('.')[-1], index)] = curve # For now, i'm just interested in the type, not the whole data path. Hence, the split returns the name after the last dot. 
    if len(curves):
        return curves
    return None
