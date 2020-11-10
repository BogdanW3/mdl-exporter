from export_mdl.utils import f2s


def save_pivot_points(fw, model):
    if len(model.objects_all):
        fw("PivotPoints %d {\n" % len(model.objects_all))
        for object in model.objects_all:
            fw("\t{%s, %s, %s},\n" % tuple(map(f2s, object.pivot)))
        fw("}\n")