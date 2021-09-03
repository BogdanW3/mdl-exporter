from typing import TextIO

from ..classes.War3Model import War3Model
from ..utils import f2s


def save_pivot_points(fw: TextIO.write, model: War3Model):
    if len(model.objects_all):
        fw("PivotPoints %d {\n" % len(model.objects_all))
        for obj in model.objects_all:
            fw("\t{%s, %s, %s},\n" % tuple(map(f2s, obj.pivot)))
        fw("}\n")
