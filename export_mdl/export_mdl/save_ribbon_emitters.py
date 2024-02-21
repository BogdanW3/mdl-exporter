from typing import TextIO

from ..classes.War3Model import War3Model


def save_ribbon_emitters(fw: TextIO.write, model: War3Model):
    for psys in model.particle_ribbon:
        psys.write_ribbon(fw, model.global_seqs, model.textures, model.materials)
