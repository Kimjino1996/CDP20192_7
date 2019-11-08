def bytes_to_int(self, bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result


def int_to_bytes(self, value, length):
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)
    result.reverse()
    return result


 print(int.from_bytes(self.read_sector(8192),byteorder='little'))
        print(self.bytes_to_int(self.read_sector(8192)))