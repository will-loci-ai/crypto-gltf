def bit_slice(num: int, start: int, stop: int, length: int = 32) -> int:
    """Returns bit slice for integer"""
    mask = 2 ** (stop - start) - 1
    shift = length - (stop - start) - start
    return (num & (mask << shift)) >> shift
