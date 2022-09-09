import re
from .mdl_reader import extract_bracket_content, extract_float_values, chunkifier
from ...classes.War3AnimationCurve import War3AnimationCurve


def parse_geoset_transformation(node_chunk: str) -> War3AnimationCurve:
    transformation = War3AnimationCurve()

    transformation_chunk = extract_bracket_content(node_chunk)
    transformation.interpolation = transformation_chunk.split(",")[0].strip()
    # globalSequenceId = -1

    points_start = transformation_chunk.find(",")
    should_chunkify = transformation_chunk.find("{") > -1
    transformation_points = re.split(',\\s*(?=\\d+:)', transformation_chunk[points_start+1:])

    for point in transformation_points:
        # print("point: " + point, should_chunkify)
        if point != '' and re.match('\\d+:', point.strip('\n\t')):
            time = int(point.split(":")[0])
            if should_chunkify:
                point_stuff = chunkifier(point)
            else:
                point_stuff = re.split("\n\t*", point.split(":")[1].strip())

            for stuff in point_stuff:
                line_start = stuff.split(" ")[0].strip('\n\t ,')
                line_values = extract_float_values(stuff)

                if len(line_values) == 4:
                    # print("float from \"%s\" =" % stuff, line_values)
                    line_values = [line_values[3], line_values[0], line_values[1], line_values[2]]

                if line_start == "InTan":
                    in_tan = line_values
                    transformation.handles_left[time] = in_tan

                if line_start == "OutTan":
                    out_tan = line_values
                    transformation.handles_right[time] = out_tan

                if re.match("\\d+", line_start):
                    values = line_values
                    transformation.keyframes[time] = values

    return transformation
