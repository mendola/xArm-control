def get_high_bits(bits: int) -> int:
        return (bits & 0xFF00) >> 8


def get_low_bits(bits: int) -> int:
        return bits & 0xFF


def degrees_to_rotation(degrees: float) -> int:
    rotation = round((degrees + 120) * 1000 / 240)
    if rotation > 1000:
            rotation = 1000
    elif rotation < 0:
            rotation = 0
    return rotation


def rotation_to_degrees(rotation: int) -> float:
    if rotation > 1000:
        rotation = 1000
    elif rotation < 0:
        rotation = 0
    degrees = (rotation * 240 / 1000) - 120
    return degrees
