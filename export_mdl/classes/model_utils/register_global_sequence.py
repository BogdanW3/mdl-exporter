from typing import Optional, Set

from export_mdl.classes.War3AnimationCurve import War3AnimationCurve


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)
