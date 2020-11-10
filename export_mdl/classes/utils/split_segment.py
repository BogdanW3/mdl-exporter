from mathutils import Vector, Quaternion


def split_segment(keyframes, type1, start, end, tolerance):
    n = float(end[0] - start[0])
    error = -1
    frame = 0
    # print('Start: %d, End: %d, Range: %f' % (start[0], end[0], n))

    for i in (i for i in range(start[0], end[0]) if i in keyframes.keys()):
        middle = keyframes[i]
        distance = 0
        t = max(0, min(1, float(i - start[0]) / n))  # Interpolation factor
        if type1 == 'Translation' or type1 == 'Scale':
            a = Vector(start[1])
            b = Vector(middle)
            c = Vector(end[1])
            delta = b - a.lerp(c, t)
            distance = delta.magnitude # Just the linear distance, for now
        elif type1 == 'Rotation':
            distance = 1 - Quaternion(middle).dot(Quaternion(start[1]).slerp(Quaternion(end[1]), t))  # Spherical distance in the range of 0-2

        if distance > error:
            error = distance
            frame = i

    if error > 0 and error > tolerance:
        middle = (frame, keyframes[frame])
        result = [middle]
        if frame != start[0] and frame != end[0]:  # Prevents infinite recursion
            result += split_segment(keyframes, type1, start, middle, tolerance)
            result += split_segment(keyframes, type1, middle, end, tolerance)
            return result

    return []
