import secrets
from time import time

import numpy as np
from crypto_gltf.encrypt.adaptive.utils import buffer_length, get_bits, put_bits
from crypto_gltf.utils.numpy_utils import array_bit_slice_eq

if __name__ == "__main__":

    for _ in range(100):
        rows = np.random.randint(1, 1000)
        cols = np.random.randint(1, 16)  # range for 3d mesh matrices
        shape = (rows, cols)
        size = shape[0] * shape[1]
        arr = (
            np.random.random_sample((shape[0] * shape[1]))
            .reshape(shape[0], shape[1], order="C")
            .astype(np.float32)
        )
        start = 0
        stop = 32
        buffer = np.zeros((size), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(arr, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)
        assert np.array_equal(arr, putarr)

    for _ in range(100):
        rows = np.random.randint(1, 1000)
        cols = np.random.randint(1, 16)  # range for 3d mesh matrices
        shape = (rows, cols)
        size = shape[0] * shape[1]
        mat = (
            np.random.random_sample((size))
            .reshape(shape[0], shape[1], order="C")
            .astype(np.float32)
        )
        start = np.random.randint(0, 31)
        stop = np.random.randint(start + 1, 32)
        buffer = np.zeros((size), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(mat, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)

    for _ in range(10):
        rows, cols = np.random.randint(1, 1000), np.random.randint(1, 1000)
        slices = 3
        start = 0
        stop = 8

        shape = (rows, cols, slices)
        size = rows * cols * slices

        mat = (
            np.random.randint(low=0, high=255, size=size)
            .reshape(shape, order="C")
            .astype(np.uint8)
        )

        buffer = np.zeros((size), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)

        assert np.array_equal(mat, putarr)

    for _ in range(10):
        rows, cols = np.random.randint(1, 1000), np.random.randint(1, 1000)
        slices = 3
        start = np.random.randint(0, 7)
        stop = np.random.randint(start + 1, 8)

        shape = (rows, cols, slices)
        size = rows * cols * slices

        mat = (
            np.random.randint(low=0, high=255, size=size)
            .reshape(shape, order="C")
            .astype(np.uint8)
        )

        bufflen = buffer_length(start, stop, rows, cols, slices)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)
