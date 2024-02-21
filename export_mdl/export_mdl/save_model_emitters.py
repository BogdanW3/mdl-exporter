from typing import TextIO, List, Dict, Set

from ..classes.War3ParticleEmitter import War3ParticleEmitter


def save_model_emitters(fw: TextIO.write, particle_systems: List[War3ParticleEmitter], global_seqs: Set[int]):
    for psys in particle_systems:
        psys.write_particle(fw, global_seqs)
