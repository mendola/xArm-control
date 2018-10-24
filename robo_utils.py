def get_high_bits(bits: int) -> int:
        return (bits & 0xFF00) >> 8


def get_low_bits(bits: int) -> int:
        return bits & 0xFF


def deg_to_bits(degrees: float) -> int:
        rotation = round((degrees + 120.0) * 1000.0 / 240.0)
        if rotation > 1000:
                rotation = 1000
        elif rotation < 0:
                rotation = 0
        return rotation


def bits_to_deg(rotation: int) -> float:
    if rotation > 1000:
        rotation = 1000
    elif rotation < 0:
        rotation = 0
    degrees = (rotation * 240 / 1000) - 120
    return degrees
