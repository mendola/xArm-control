def get_high_bits(val):
        return (val & 0xFF00) >> 8

def get_low_bits(val):
        return val & 0xFF

def deg_to_bits(degrees):
        val = round((degrees + 120.0) * 1000.0 / 240.0)
        if val > 1000:
                val = 1000
        elif val < 0:
                val = 0
        return val

def bits_to_deg(bits):
    if bits > 1000:
        bits = 1000
    elif bits < 0:
        bits = 0
    deg = float(bits) * 240 / 1000 - 120
    return deg