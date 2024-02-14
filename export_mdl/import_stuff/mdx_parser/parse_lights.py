from typing import List

from .parse_timeline import parse_timeline
from ... import constants
from ...classes.War3Light import War3Light
from . import binary_reader
from .parse_node import parse_node


def parse_lights(data: bytes) -> List[War3Light]:
    data_size = len(data)
    reader = binary_reader.Reader(data)

    nodes: List[War3Light] = []
    while reader.offset < data_size:
        inclusive_size = reader.getf('<I')[0]
        node_data_size = inclusive_size - 4
        node_data = data[reader.offset: reader.offset + node_data_size]
        reader.skip(node_data_size)

        r = binary_reader.Reader(node_data)
        data_size_chunk = len(node_data)
        node = War3Light("")
        parse_node(r, node)

        print("  reading light static data!")
        node.light_type = ('Omnidirectional', 'Directional', 'Ambient')[r.get_int()]
        node.atten_start = r.get_float()
        node.atten_end = r.get_float()
        node.color = r.get_floats(3)
        node.intensity = r.get_float()
        node.amb_color = r.get_floats(3)
        node.amb_intensity = r.get_float()
        print(
            ("   pos: [%.2f, %.2f, %.2f]"     % tuple(node.pivot)) +
            (", light_type: %s"             % node.light_type) +
            (", atten_start: %.2f"           % node.atten_start) +
            (", atten_end: %.2f"             % node.atten_end) +
            (", color: [%.2f, %.2f, %.2f]"     % node.color) +
            (", intensity: %.2f"             % node.intensity) +
            (", amb_color: [%.2f, %.2f, %.2f]" % node.amb_color) +
            (", amb_intensity: %.2f"          % node.amb_intensity))

        while r.offset < data_size_chunk:
            chunk_id = r.getid(constants.SUB_CHUNKS_LIGHT)

            if chunk_id == constants.CHUNK_LIGHT_ATTENUATION_START:
                node.atten_start_anim = parse_timeline(r, '<f')
            elif chunk_id == constants.CHUNK_LIGHT_ATTENUATION_END:
                node.atten_end_anim = parse_timeline(r, '<f')
            elif chunk_id == constants.CHUNK_LIGHT_COLOR:
                node.color_anim = parse_timeline(r, '<3f')
            elif chunk_id == constants.CHUNK_LIGHT_INTENSITY:
                node.intensity_anim = parse_timeline(r, '<f')
            elif chunk_id == constants.CHUNK_LIGHT_AMBIENT_COLOR:
                node.amb_color_anim = parse_timeline(r, '<3f')
            elif chunk_id == constants.CHUNK_LIGHT_AMBIENT_INTENSITY:
                node.amb_intensity_anim = parse_timeline(r, '<f')
            elif chunk_id == constants.CHUNK_LIGHT_VISIBILITY:
                node.visibility = parse_timeline(r, '<f')

        nodes.append(node)
    return nodes


def parse_lights1(data: bytes) -> List[War3Light]:
    data_size = len(data)
    reader = binary_reader.Reader(data)

    nodes: List[War3Light] = []
    while reader.offset < data_size:
        inclusive_size = reader.getf('<I')[0]
        node_data_size = inclusive_size - 4
        node_data = data[reader.offset: reader.offset + node_data_size]
        reader.skip(node_data_size)

        r = binary_reader.Reader(node_data)
        data_size_chunk = len(node_data)
        node = War3Light("")
        parse_node(r, node)
        nodes.append(node)
    return nodes

