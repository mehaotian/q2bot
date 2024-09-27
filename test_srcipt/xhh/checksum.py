def c0(v):
    return c1(v) ^ c2(v) ^ c3(v)

def c1(v):
    return c2(c3(convert_byte(v)))

def c2(v):
    return c3(convert_byte(v))

def c3(v):
    return convert_byte(v) ^ v

def convert_byte(v):
    return (v << 1) ^ 0x1b if v & 0x80 else v << 1

def checksum(data):
    return sum([
        c0(data[0]) ^ c1(data[1]) ^ c2(data[2]) ^ c3(data[3]),
        c3(data[0]) ^ c0(data[1]) ^ c1(data[2]) ^ c2(data[3]),
        c2(data[0]) ^ c3(data[1]) ^ c0(data[2]) ^ c1(data[3]),
        c1(data[0]) ^ c2(data[1]) ^ c3(data[2]) ^ c0(data[3])
    ]) % 100
