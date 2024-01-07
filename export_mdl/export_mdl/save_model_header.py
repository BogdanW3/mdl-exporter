from typing import TextIO

from ..classes.War3Model import War3Model
from ..utils import float2str, calc_bounds_radius


def save_model_header(fw: TextIO.write, model: War3Model):
    fw("Model \"%s\" {\n" % model.name)
    if len(model.geosets):
        fw("\tNumGeosets %d,\n" % len(model.geosets))
    if len(model.bones):
        fw("\tNumBones %d,\n" % len(model.bones))
    if len(model.attachments):
        fw("\tNumAttachments %d,\n" % len(model.attachments))
    if len(model.particle_systems):
        fw("\tNumParticleEmitters %d,\n" % len(model.particle_systems))
    if len(model.particle_systems2):
        fw("\tNumParticleEmitters2 %d,\n" % len(model.particle_systems2))
    if len(model.particle_ribbon):
        fw("\tNumRibbonEmitters %d,\n" % len(model.particle_ribbon))
    if len(model.event_objects):
        fw("\tNumEvents %d,\n" % len(model.event_objects))
    if len(model.geoset_anims):
        fw("\tNumGeosetAnims %d,\n" % len(model.geoset_anims))
    if len(model.lights):
        fw("\tNumLights %d,\n" % len(model.lights))
    if len(model.helpers):
        fw("\tNumHelpers %d,\n" % len(model.helpers))

    fw("\tBlendTime %d,\n" % 150)
    fw("\tMinimumExtent { %s, %s, %s },\n" % tuple(map(float2str, model.global_extents_min)))
    fw("\tMaximumExtent { %s, %s, %s },\n" % tuple(map(float2str, model.global_extents_max)))
    fw("\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(model.global_extents_min, model.global_extents_max)))
    fw("}\n")
