from typing import TextIO

from ..classes.War3Model import War3Model


def save_particle_emitters(fw: TextIO.write, model: War3Model):
    for psys in model.particle_systems2:
        psys.write_particle(fw, model.object_indices, model.global_seqs, model.textures)
