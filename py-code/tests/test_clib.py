import secrets

import numpy as np
from py_code.encrypt.adaptive.utils import buffer_length, get_bits, put_bits
from py_code.utils.numpy_utils import array_bit_slice_eq


def test_put_get_inversion32():
    """Test that put/get are inverses if slice is the whole float32"""
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

        bufflen = buffer_length(start, stop, rows, cols)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(arr, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)
        assert np.array_equal(arr, putarr)


def test_put_get_varied_slice32():
    """Test that put/get are inverses for varied bit slices for float32"""
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

        bufflen = buffer_length(start, stop, rows, cols)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(mat, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)


def test_put_get_inversion8_3D():
    """Test that put/get are inverses for get_bits if slice is the whole 3D uint8 matrix"""

    for _ in range(10):
        rows, cols = np.random.randint(1, 2048), np.random.randint(1, 2048)
        slices = np.random.randint(1, 3)

        shape = (rows, cols, slices)
        size = rows * cols * slices

        mat = (
            np.random.randint(low=0, high=255, size=size)
            .reshape(shape, order="C")
            .astype(np.uint8)
        )

        start = 0
        stop = 8
        bufflen = buffer_length(start, stop, rows, cols, slices)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr_interim = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr_interim, buffer, start, stop)

        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")
        get_bits(putarr_interim, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)
        assert np.array_equal(mat, putarr)


def test_put_get_varied_slice8_3D():
    """Test that put/get are inverses for varied bit slices for 3D uint8"""

    for _ in range(10):
        rows, cols = np.random.randint(1, 2048), np.random.randint(1, 2048)
        slices = np.random.randint(1, 3)
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
        putarr_interim = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr_interim, buffer, start, stop)

        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")
        get_bits(putarr_interim, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)


def test_put_get_inversion8_2D():
    """Test that put/get are inverses if slice is the whole 2D uint8"""

    for _ in range(10):
        rows, cols = np.random.randint(1, 2048), np.random.randint(1, 2048)

        shape = (rows, cols)
        size = rows * cols
        mat = (
            np.random.randint(low=0, high=255, size=size)
            .reshape(shape, order="C")
            .astype(np.uint8)
        )

        start = 0
        stop = 8
        bufflen = buffer_length(start, stop, rows, cols)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr_interim = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr_interim, buffer, start, stop)

        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")
        get_bits(putarr_interim, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)

        assert np.array_equal(mat, putarr)


def test_put_get_varied_slice8_2D():
    """Test that put/get are inverses for varied bit slices for 2D uint8"""

    for _ in range(10):
        rows, cols = np.random.randint(1, 2048), np.random.randint(1, 2048)
        start = np.random.randint(0, 7)
        stop = np.random.randint(start + 1, 8)

        shape = (rows, cols)
        size = rows * cols

        mat = (
            np.random.randint(low=0, high=255, size=size)
            .reshape(shape, order="C")
            .astype(np.uint8)
        )

        bufflen = buffer_length(start, stop, rows, cols)
        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr_interim = np.zeros(shape, dtype=np.uint8, order="C")

        get_bits(mat, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr_interim, buffer, start, stop)

        buffer = np.zeros((bufflen), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.uint8, order="C")
        get_bits(putarr_interim, buffer, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)
