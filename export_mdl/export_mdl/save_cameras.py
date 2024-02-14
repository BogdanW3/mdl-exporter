from typing import TextIO

from ..classes.War3Model import War3Model


def save_cameras(fw: TextIO.write, model: War3Model, settings):
    for camera in model.cameras:
        camera.write_camera(fw, model.global_seqs)
